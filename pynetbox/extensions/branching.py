"""
pynetbox extension for the [NetBox branching plugin][branching].

[branching]: https://github.com/netboxlabs/netbox-branching

Wires up the plugin's per-branch detail actions (`merge`, `sync`, `revert`,
`archive`) as Pythonic methods on the `Branches` record, and marks the JSON
fields on `Changes` (ChangeDiff) so they round-trip as Python dicts/lists
instead of being mangled into nested `Record` objects.

## Usage

```python
import pynetbox
from pynetbox.extensions import BranchingExtension

nb = pynetbox.api(
    "http://localhost:8000",
    token="...",
    extensions=[BranchingExtension],
)

branch = nb.plugins.branching.branches.create(name="my-branch")
# (poll branch.status until 'ready' — see docs/branching.md)

# Synchronize the branch from main, merge it, or revert a merged branch.
# Each returns a `Jobs` record representing the background job NetBox
# enqueues to do the actual work.
sync_job = branch.sync(commit=True)
merge_job = branch.merge(commit=True)
revert_job = branch.revert(commit=True)

# Archive a merged branch (no background job — returns the updated branch).
branch.archive()
```

## Conflict handling

`sync` and `merge` return HTTP 409 when conflicting `ChangeDiff` objects
exist and have not been acknowledged. This surfaces in pynetbox as a
`RequestError`; inspect `error.error` for the conflict payload, or pass
`acknowledge_conflicts=True` after reviewing the conflicts to proceed.

```python
import pynetbox

try:
    branch.merge(commit=True)
except pynetbox.RequestError as exc:
    if exc.req.status_code == 409:
        # exc.error is the conflicts payload; inspect, then either resolve
        # or acknowledge and retry.
        branch.merge(commit=True, acknowledge_conflicts=True)
    else:
        raise
```

## Listing branchable models

The plugin also exposes a `branchable-models` list endpoint enumerating
which NetBox models support branching:

```python
for model in nb.plugins.branching.branchable_models.all():
    print(model.app_label, model.model)
```
"""

from pynetbox.core.extension import Extension
from pynetbox.core.query import Request
from pynetbox.core.response import JsonField, Record
from pynetbox.models.core import Jobs


def _post_detail(parent, action_name, data=None, return_cls=None, api=None):
    """POST to /<parent>/<id>/<action>/ and wrap the response.

    Used by Branches.{merge,sync,revert,archive}. We don't go through
    DetailEndpoint here because we want to (a) return a different Record
    class than the parent endpoint's, and (b) keep the call sites as
    simple method invocations rather than `.create()` chains.
    """
    url = "{}/{}/{}/".format(parent.endpoint.url, parent.id, action_name)
    resp = Request(
        base=url,
        token=parent.api.token,
        http_session=parent.api.http_session,
    ).post(data or {})
    if return_cls is None:
        return resp
    return return_cls(resp, api or parent.api, parent.endpoint)


class Branches(Record):
    """A NetBox branch.

    Adds the plugin-specific detail actions as direct methods. Each returns
    a `Jobs` record for the background job NetBox enqueues, except
    `archive`, which returns the updated `Branches` record.
    """

    def sync(self, commit=True, acknowledge_conflicts=False):
        """Enqueue a background job to sync this branch from main.

        ## Parameters

        * **commit** (bool): If False, perform a dry-run without persisting
            changes. Defaults to True.
        * **acknowledge_conflicts** (bool): Proceed even when unresolved
            `ChangeDiff` conflicts exist. Defaults to False.

        ## Returns
        A `Jobs` record for the enqueued sync job.

        ## Raises
        `RequestError`: 409 if conflicts exist and have not been
        acknowledged; 403 if the user lacks `sync_branch` permission.
        """
        return _post_detail(
            self,
            "sync",
            data={"commit": commit, "acknowledge_conflicts": acknowledge_conflicts},
            return_cls=Jobs,
        )

    def merge(self, commit=True, acknowledge_conflicts=False):
        """Enqueue a background job to merge this branch into main.

        ## Parameters

        * **commit** (bool): If False, perform a dry-run without persisting
            changes. Defaults to True.
        * **acknowledge_conflicts** (bool): Proceed even when unresolved
            `ChangeDiff` conflicts exist. Defaults to False.

        ## Returns
        A `Jobs` record for the enqueued merge job.

        ## Raises
        `RequestError`: 409 if conflicts exist and have not been
        acknowledged; 403 if the user lacks `merge_branch` permission;
        400 if the branch is not in a mergeable state.
        """
        return _post_detail(
            self,
            "merge",
            data={"commit": commit, "acknowledge_conflicts": acknowledge_conflicts},
            return_cls=Jobs,
        )

    def revert(self, commit=True):
        """Enqueue a background job to revert this merged branch.

        ## Parameters

        * **commit** (bool): If False, perform a dry-run without persisting
            changes. Defaults to True.

        ## Returns
        A `Jobs` record for the enqueued revert job.

        ## Raises
        `RequestError`: 400 if the branch has not been merged; 403 if the
        user lacks `revert_branch` permission.
        """
        return _post_detail(
            self, "revert", data={"commit": commit}, return_cls=Jobs
        )

    def archive(self):
        """Archive this merged branch, deprovisioning its schema.

        Returns the updated `Branches` record. Unlike sync/merge/revert,
        archive is synchronous — no background job is enqueued.

        ## Raises
        `RequestError`: 400 if the branch has not been merged or cannot be
        archived; 403 if the user lacks `archive_branch` permission.
        """
        updated = _post_detail(self, "archive")
        # Refresh the local record with the server's view of the branch.
        self._parse_values(updated)
        return self

    @property
    def changes(self):
        """Return this branch's `ChangeDiff`s as a `RecordSet`.

        Convenience for ``nb.plugins.branching.changes.filter(
        branch_id=branch.id)``. `ChangeDiff` is a top-level endpoint
        on the branching plugin, so this delegates there with the
        branch filter applied. Each item is a `Changes` record.
        """
        return self.api.plugins.branching.changes.filter(branch_id=self.id)


class BranchEvents(Record):
    """A read-only branch event (creation, sync, merge, etc.)."""

    pass


class Changes(Record):
    """A single object change recorded against a branch.

    The plugin's `ChangeDiff` model has several JSON-typed fields that the
    default pynetbox deserialization would otherwise mangle into nested
    `Record` objects. Marking them with `JsonField` keeps them as plain
    dicts/lists.
    """

    conflicts = JsonField
    diff = JsonField
    original_data = JsonField
    modified_data = JsonField
    current_data = JsonField


class BranchableModels(Record):
    """A NetBox model that supports branching.

    The `branchable-models` endpoint returns lightweight `{app_label,
    model, verbose_name, verbose_name_plural}` entries without an `id` or
    `url`, so this record acts purely as a typed wrapper.
    """

    pass


class _Models:
    """Namespace for endpoint name → Record class lookups.

    pynetbox's endpoint resolver does ``getattr(models, "Branches", Record)``
    for ``nb.plugins.branching.branches``, so each attribute below is named
    after the title-cased endpoint name (dashes become CamelCase).
    """

    Branches = Branches
    BranchEvents = BranchEvents
    Changes = Changes
    BranchableModels = BranchableModels


class BranchingExtension(Extension):
    """pynetbox extension for the netbox-branching plugin.

    Register with:

    ```python
    import pynetbox
    from pynetbox.extensions import BranchingExtension

    nb = pynetbox.api(url, token="...", extensions=[BranchingExtension])
    ```

    See the module docstring for usage examples.
    """

    plugin_name = "branching"
    models = _Models
    content_types = {
        "netbox_branching.branch": Branches,
        "netbox_branching.branchevent": BranchEvents,
        "netbox_branching.changediff": Changes,
    }
