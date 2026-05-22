# Branching Plugin

The [NetBox branching plugin](https://github.com/netboxlabs/netbox-branching) lets you create branches in NetBox, much like a version control system. Changes made within a branch are isolated from the main schema and can later be merged.

!!! note "Plugin required"
    These methods only work when the branching plugin is installed and enabled in your NetBox instance. They have no effect on a stock NetBox installation.

## Registering the Extension

pynetbox ships a `BranchingExtension` that wires up the plugin's per-branch detail actions (`merge`, `sync`, `revert`, `archive`) and marks the JSON columns on `ChangeDiff` so they round-trip as Python dicts/lists. Register it with `pynetbox.api(extensions=[...])`:

```python
import pynetbox
from pynetbox.extensions import BranchingExtension

nb = pynetbox.api(
    "http://localhost:8000",
    token="your-token-here",
    extensions=[BranchingExtension],
)
```

Without the extension, `nb.plugins.branching.*` still works for basic CRUD, but the methods described below (`branch.merge()`, etc.) and the JSON-field handling on `Changes` are unavailable. See [Extensions](extensions.md) for the framework's general design.

## Branch Actions

With the extension registered, every `Branches` record exposes the plugin's detail actions as direct methods. `sync`, `merge`, and `revert` each return a `Jobs` record for the background job NetBox enqueues; `archive` is synchronous and returns the updated `Branches` record.

```python
branch = nb.plugins.branching.branches.create(name="my-branch")
# (poll branch.status until 'ready' — see the section further down)

# Dry-run a merge to see what would happen.
dry_run = branch.merge(commit=False)

# Sync the branch from main, then merge it.
sync_job = branch.sync(commit=True)
merge_job = branch.merge(commit=True)

# Revert a previously merged branch.
revert_job = branch.revert(commit=True)

# Archive a merged branch, deprovisioning its schema.
branch.archive()
```

### Conflict Handling

`sync` and `merge` return HTTP 409 when conflicting `ChangeDiff`s exist and have not been acknowledged. This surfaces in pynetbox as a `RequestError`; the response body (with the list of conflicts) is on `error.error`. Resolve the conflicts or pass `acknowledge_conflicts=True` to proceed.

```python
import pynetbox

try:
    branch.merge(commit=True)
except pynetbox.RequestError as exc:
    if exc.req.status_code == 409:
        # exc.error contains the conflicts payload. Inspect, then either
        # resolve the conflicts and retry, or acknowledge and proceed.
        branch.merge(commit=True, acknowledge_conflicts=True)
    else:
        raise
```

## Inspecting Changes

`ChangeDiff` rows are exposed at `nb.plugins.branching.changes`. The extension marks `diff`, `original_data`, `modified_data`, `current_data`, and `conflicts` as JSON fields so they're returned as plain Python dicts/lists instead of being mangled into nested records.

```python
for change in nb.plugins.branching.changes.filter(branch_id=branch.id):
    print(change.object_type, change.action, change.diff)
```

## Branchable Models

The plugin's `branchable-models` list endpoint enumerates which NetBox models support branching (including plugin-supplied models):

```python
for model in nb.plugins.branching.branchable_models.all():
    print(model.app_label, model.model)
```

## Activating a Branch

`Api.activate_branch()` is a context manager that adds the `X-NetBox-Branch` header to outgoing requests so they operate against the branch's schema. The header is removed when the `with` block exits.

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token-here',
)

# Look up an existing branch
branch = nb.plugins.branching.branches.get(1)

# All NetBox operations inside the block run against this branch
with nb.activate_branch(branch):
    sites = nb.dcim.sites.all()
    # Create, update, and delete calls here only affect the branch's schema
```

The argument must be a branch `Record` (the object returned by the branches endpoint). Passing anything else raises `ValueError`.

## Waiting for a Branch to be Ready

Newly created branches are not immediately ready; NetBox runs a background job to provision the branch's schema. Likewise, merges and reverts are asynchronous. The [tenacity](https://github.com/jd/tenacity) library is a convenient way to poll a branch until it reaches a target status:

```bash
pip install tenacity
```

```python
from tenacity import retry, retry_if_result, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(30),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_result(lambda ready: not ready),
)
def wait_for_branch_status(branch, target_status):
    """Poll until ``branch`` reaches ``target_status``."""
    branch = nb.plugins.branching.branches.get(branch.id)
    return str(branch.status) == target_status


# Create a branch and wait for it to become Ready
branch = nb.plugins.branching.branches.create(name='my-branch')
wait_for_branch_status(branch, 'Ready')

branch = nb.plugins.branching.branches.get(branch.id)
print(f"Branch is ready! Status: {branch.status}")
```

The helper above will:

1. Re-fetch the branch and compare its status to the target.
2. Retry with exponential backoff (4–60 seconds between attempts) until the target is reached.
3. Give up after 30 attempts.

Exponential backoff strikes a balance between checking frequently enough to catch quick transitions and avoiding excessive load on the NetBox server.
