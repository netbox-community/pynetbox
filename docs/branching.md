# Branching Plugin

The [NetBox branching plugin](https://github.com/netboxlabs/netbox-branching) lets you create branches in NetBox, much like a version control system. Changes made within a branch are isolated from the main schema and can later be merged.

!!! note "Plugin required"
    These methods only work when the branching plugin is installed and enabled in your NetBox instance. They have no effect on a stock NetBox installation.

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
