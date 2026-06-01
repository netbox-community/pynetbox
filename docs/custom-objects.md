# Custom Objects Plugin

The [NetBox Custom Objects plugin](https://github.com/netboxlabs/netbox-custom-objects) lets you define user-defined object types (and their fields) at runtime, then create instances of those types under `/api/plugins/custom-objects/<slug>/`.

!!! note "Plugin required"
    These methods only work when the custom-objects plugin is installed and enabled in your NetBox instance. They have no effect on a stock NetBox installation.

## Registering the Extension

pynetbox ships a `CustomObjectsExtension` that marks the plugin's JSON columns so they round-trip as Python dicts (the fix for [#751](https://github.com/netbox-community/pynetbox/issues/751)), resolves dynamic per-type endpoints, and adds helpers for the plugin's schema preview/apply routes. Register it with `pynetbox.api(extensions=[...])`:

```python
import pynetbox
from pynetbox.extensions import CustomObjectsExtension

nb = pynetbox.api(
    "http://localhost:8000",
    token="your-token-here",
    extensions=[CustomObjectsExtension],
)
```

Without the extension, `nb.plugins.custom_objects.*` still works for basic CRUD, but JSON columns like `related_object_filter` and `schema_document` are mangled into nested `Record` objects (and effectively lost), and per-type endpoints return generic `Record` instances instead of typed `CustomObject` records. See [Extensions](extensions.md) for the framework's general design.

## Custom Object Types and Fields

`CustomObjectTypes` and `CustomObjectTypeFields` deserialize the plugin's JSON-typed columns as plain Python dicts/lists:

```python
cot = nb.plugins.custom_objects.custom_object_types.get(1)

# JSON columns round-trip as plain dicts
cot.schema_document                         # dict
cot.fields[0].related_object_filter         # dict (fix for #751)
cot.fields[0].related_object_type           # dict {"id", "app_label", "model"}
```

`fields` is a nested list of `CustomObjectTypeFields` records, so attribute access on each item works as expected.

!!! note "`related_object_types` (plural)"
    On polymorphic Object/MultiObject fields the server returns `related_object_types` as a list of `{id, app_label, model}` dicts. This field is not marked `JsonField`, so pynetbox wraps each list item in a base `Record`, so `field.related_object_types[0].app_label` works, but `isinstance(field.related_object_types[0], dict)` is `False` — unlike the singular `related_object_type`, which is marked `JsonField` and round-trips as a plain dict. (Marking a list-valued column `JsonField` keeps its items as plain dicts.)

## Custom Objects (per-type endpoints)

Each Custom Object Type exposes a list endpoint at `/api/plugins/custom-objects/<slug>/`. Attribute access on `nb.plugins.custom_objects` returns a typed `CustomObject` record for any endpoint name (the underscore-to-dash convention applies, so a COT with slug `cidr-list` is reached as `nb.plugins.custom_objects.cidr_list`):

```python
for obj in nb.plugins.custom_objects.cidr_list.all():
    print(obj.name, obj.custom_object_type.slug)

# Create via the dynamic endpoint
new = nb.plugins.custom_objects.cidr_list.create(name="ours", prefix=42)
```

`CustomObject.custom_object_type` resolves to a `CustomObjectTypes` record, so `obj.custom_object_type.slug` works without an extra fetch when the per-type serializer includes it.

## Linked Objects

`linked-objects/` reports which custom objects link to a given NetBox object via an Object/MultiObject field:

```python
hits = nb.plugins.custom_objects.linked_objects.filter(
    object_type="dcim.device", object_id=5,
)
for row in hits:
    print(row.custom_object_type["slug"], row.field_name, row.object["id"])
```

Both `custom_object_type` and `object` come back as plain dicts — the target type isn't fixed (it can be any NetBox model), so the extension intentionally doesn't try to wrap them in typed records.

## Schema Preview and Apply

The plugin exposes two non-CRUD endpoints for declarative schema management:

* **`POST /schema/preview/`** — diff a schema document against the current DB, no changes applied.
* **`POST /schema/apply/`** — apply the diff (optionally allowing destructive operations).

pynetbox wraps both as module-level helpers:

```python
from pynetbox.extensions.custom_objects import schema_apply, schema_preview

doc = {
    "schema_version": "1",
    "types": [
        {
            "name": "my_cot",
            "slug": "my-cot",
            "fields": [
                {"id": 1, "name": "label", "type": "text", "primary": True, "required": True},
            ],
        }
    ],
}

# Dry-run: returns {"diffs": [...]}
diff = schema_preview(nb, doc)

# Apply: returns {"applied": True, "diffs": [...]}
result = schema_apply(nb, doc, allow_destructive=False)
```

The plugin returns HTTP 409 when the document contains destructive changes (field removals) and `allow_destructive=False`; pynetbox surfaces this as a `RequestError`. The conflict payload is on `exc.error` and includes the destructive COT slugs:

```python
import pynetbox

try:
    schema_apply(nb, doc)
except pynetbox.RequestError as exc:
    if exc.req.status_code == 409:
        # exc.error: {"error": "destructive_changes", "destructive_slugs": [...]}
        # After reviewing, re-apply with allow_destructive=True.
        schema_apply(nb, doc, allow_destructive=True)
    else:
        raise
```

Other server-side errors map to `RequestError` as well: 400 for invalid documents, circular COT dependencies, or unresolvable FK targets; 403 if the user lacks `add_customobjecttype` and `change_customobjecttype` permissions.

## Generic Foreign Key resolution

The extension registers content-type mappings for `netbox_custom_objects.customobjecttype` and `netbox_custom_objects.customobjecttypefield`, so any other endpoint that references these models via a generic FK (for example, a tag scoped to a Custom Object Type) deserializes the nested object into the right typed record.
