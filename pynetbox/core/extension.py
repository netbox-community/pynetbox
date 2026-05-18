"""
Extension framework for pynetbox.

Lets third-party NetBox plugins ship custom ``Record`` subclasses and
content-type mappings without modifying pynetbox itself.

An extension is any object (typically a class) exposing:

* ``plugin_name`` (str): the plugin's slug as it appears under ``nb.plugins``
  (e.g. ``"branching"`` for ``nb.plugins.branching``). Underscores in the
  attribute access map to dashes in the URL, matching the existing
  ``PluginsApp`` convention.
* ``models``: a namespace (module, class, or any object) from which
  ``Record`` subclasses can be resolved by title-cased endpoint name —
  the same lookup used for built-in apps. For ``nb.plugins.<x>.branches``
  pynetbox will look up ``models.Branches``.
* ``content_types`` (dict, optional): maps NetBox content-type strings
  (e.g. ``"netbox_branching.branch"``) to ``Record`` subclasses, so the
  classes are used when resolving polymorphic nested objects.

## Example

```python
from pynetbox import api, Extension, JsonField
from pynetbox.core.response import Record
from pynetbox.core.endpoint import DetailEndpoint


class Branches(Record):
    @property
    def merge(self):
        return DetailEndpoint(self, "merge")


class BranchingModels:
    Branches = Branches


class BranchingExtension(Extension):
    plugin_name = "branching"
    models = BranchingModels


nb = api("http://localhost:8000", token="...", extensions=[BranchingExtension])
branch = nb.plugins.branching.branches.get(1)
branch.merge.create(commit=True)
```
"""


class Extension:
    """Base class for pynetbox extensions.

    Subclassing is optional — any object with the required attributes is
    accepted. The base class exists so extension authors have an explicit
    contract to target and so ``isinstance`` checks are available to
    downstream code that wants them.
    """

    plugin_name: str = ""
    models = None
    content_types: dict = {}
