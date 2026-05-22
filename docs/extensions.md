# Extensions

pynetbox's extension framework lets you (or a plugin author) register custom `Record` subclasses, JSON-field markers, and content-type mappings for NetBox plugins — without modifying pynetbox itself.

Extensions are opt-in and passed in explicitly when constructing the API client:

```python
import pynetbox
from pynetbox.extensions import BranchingExtension

nb = pynetbox.api(
    "http://localhost:8000",
    token="your-token-here",
    extensions=[BranchingExtension],
)
```

Plugin endpoints that an extension covers are automatically deserialized into the extension's `Record` subclasses, and any content types the extension registers participate in generic-FK resolution across the whole client.

## Shipped Extensions

pynetbox ships a small set of extensions for popular NetBox plugins. These live under `pynetbox.extensions`.

| Plugin | Extension | Docs |
|---|---|---|
| [netbox-branching](https://github.com/netboxlabs/netbox-branching) | `pynetbox.extensions.BranchingExtension` | [Branching](branching.md) |
| [netbox-custom-objects](https://github.com/netboxlabs/netbox-custom-objects) | `pynetbox.extensions.CustomObjectsExtension` | [Custom Objects](custom-objects.md) |

If you write or maintain an extension for a NetBox plugin that's widely used and want to upstream it, open an issue on the pynetbox repo.

## Writing your own Extension

An extension is any object exposing three attributes. Subclassing `pynetbox.Extension` is optional — it just gives you a typed base to target.

```python
from pynetbox import Extension
from pynetbox.core.endpoint import DetailEndpoint
from pynetbox.core.response import JsonField, Record


class Notes(Record):
    # Mark a JSON dict column so pynetbox doesn't mangle it into a nested Record.
    metadata = JsonField

    @property
    def render(self):
        # Expose a per-object sub-route like /notes/{id}/render/.
        return DetailEndpoint(self, "render")


class NotesModels:
    # Attribute names match the title-cased endpoint name. pynetbox looks up
    # ``getattr(models, "Notes", Record)`` for the endpoint
    # ``nb.plugins.notes.notes``.
    Notes = Notes


class NotesExtension(Extension):
    plugin_name = "notes"                 # matches nb.plugins.notes
    models = NotesModels
    content_types = {                     # optional; merged into the GFK mapper
        "notes.note": Notes,
    }
```

For real shipped extensions, see `pynetbox/extensions/branching.py` and `pynetbox/extensions/custom_objects.py`.

### `plugin_name`

The plugin's slug as it appears under `nb.plugins`. Attribute access uses underscores while the URL slug uses dashes, matching pynetbox's existing convention: `plugin_name = "custom_objects"` matches both `nb.plugins.custom_objects` and `/api/plugins/custom-objects/`.

### `models`

A namespace — a module, a class, or any object — from which `Record` subclasses are looked up by title-cased endpoint name. For `nb.plugins.<plugin>.foo_bars` pynetbox does `getattr(models, "FooBars", Record)`, so name your subclasses to match.

Common things to put on a Record subclass:

- **`JsonField` markers** for columns that are JSON dicts/lists. Without this, pynetbox tries to coerce a dict-typed field into a nested `Record` and the data is lost. (See `Changes` in `pynetbox/extensions/branching.py` for an example.)
- **`DetailEndpoint` properties** for per-object sub-routes like `/foo/{id}/run/` or `/foo/{id}/render/`.
- **Custom methods** for plugin-specific actions, returning whatever record type the response represents.

### `content_types` (optional)

A mapping of NetBox content-type strings (e.g. `"netbox_branching.branch"`) to your `Record` subclasses. These are merged into a per-instance copy of pynetbox's built-in `CONTENT_TYPE_MAPPER`, so polymorphic nested objects (generic foreign keys) deserialize into your classes.

### Caveats

- **Scope is limited to plugins** under `nb.plugins.*`. Extensions cannot override built-in apps (dcim, ipam, etc.).
- **No auto-discovery.** Extensions are always passed in explicitly to `pynetbox.api(extensions=[...])`. If you want a third-party package to ship an extension, document the import path users should pass in.
- **One extension per `plugin_name`** per API instance. If two extensions claim the same plugin name, the later one wins.
