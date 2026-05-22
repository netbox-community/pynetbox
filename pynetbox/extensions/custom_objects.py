"""
pynetbox extension for the [NetBox Custom Objects plugin][custom-objects].

[custom-objects]: https://github.com/netboxlabs/netbox-custom-objects

Wires up the plugin's records with the right JSON-field markers (so columns
like ``related_object_filter`` and ``schema_document`` round-trip as plain
dicts/lists), provides helpers for the plugin's non-CRUD endpoints
(``schema/preview/``, ``schema/apply/``, ``linked-objects/``), and falls
back to a ``CustomObject`` record for dynamic per-type endpoints
(``/api/plugins/custom-objects/<slug>/``).

## Usage

```python
import pynetbox
from pynetbox.extensions import CustomObjectsExtension

nb = pynetbox.api(
    "http://localhost:8000",
    token="...",
    extensions=[CustomObjectsExtension],
)

# Custom Object Types: schema_document and fields are JSON-typed.
cot = nb.plugins.custom_objects.custom_object_types.get(1)
cot.schema_document            # dict, not a Record
cot.fields[0].related_object_filter  # dict, not '' (see issue #751)

# Per-type custom objects: any attribute not statically known on the
# extension resolves to a CustomObject record class.
for obj in nb.plugins.custom_objects.cidr_list.all():
    print(obj.name, obj.serialize())

# linked-objects: standard filter() semantics.
hits = nb.plugins.custom_objects.linked_objects.filter(
    object_type="dcim.device", object_id=5,
)

# schema/preview and schema/apply: module-level helpers.
from pynetbox.extensions.custom_objects import schema_preview, schema_apply

diff = schema_preview(nb, {"schema_version": "1", "types": [...]})
result = schema_apply(nb, {"schema_version": "1", "types": [...]},
                      allow_destructive=False)
```
"""

from pynetbox.core.extension import Extension
from pynetbox.core.query import Request
from pynetbox.core.response import JsonField, Record

def _plugin_request(api, path):
    """Build a `Request` bound to a plugin sub-path under custom-objects.

    `path` is appended verbatim to ``<base>/plugins/custom-objects/`` and
    must include the trailing slash NetBox expects.
    """
    slug = CustomObjectsExtension.plugin_name.replace("_", "-")
    base = "{}/plugins/{}/{}".format(api.base_url, slug, path)
    return Request(base=base, token=api.token, http_session=api.http_session)


class CustomObjectTypeFields(Record):
    """A field definition on a Custom Object Type.

    Both `related_object_filter` (issue #751) and `related_object_type`
    (``{id, app_label, model}`` from the plugin's SerializerMethodField)
    are dict-valued and marked so they round-trip as plain dicts.

    The plural `related_object_types` is a list whose server-side items
    are ``{id, app_label, model}`` dicts. `JsonField` only applies to
    dict values, so list items deserialize into base `Record`s —
    ``.id`` / ``.app_label`` / ``.model`` remain accessible.
    """

    related_object_filter = JsonField
    related_object_type = JsonField


class CustomObjectTypes(Record):
    """A Custom Object Type definition.

    `schema_document` is a JSON blob (the document the plugin uses to
    declaratively reconstruct a type's schema) and is marked so it
    survives the round trip. `fields` is a list of nested
    `CustomObjectTypeFields` records, which the existing list-parser
    handles when given a class as the list element.
    """

    schema_document = JsonField
    fields = [CustomObjectTypeFields]


class CustomObject(Record):
    """A single custom object of an arbitrary user-defined type.

    The serializer is generated per type and the response shape depends
    on the type's field definitions, so this class intentionally adds no
    new field-level handling beyond marking the optional `_context`
    metadata column (which the server emits as a nested dict when the
    type has designated context fields).

    The nested `custom_object_type` attribute resolves to a
    `CustomObjectTypes` record so attribute access (``obj.custom_object_type.slug``)
    works as expected.
    """

    custom_object_type = CustomObjectTypes
    _context = JsonField


class LinkedObjects(Record):
    """An entry from the ``linked-objects/`` endpoint.

    Each row reports a custom object that references some other NetBox
    object via an Object/MultiObject field, in the shape::

        {
            "custom_object_type": {...},
            "field_name": "...",
            "object": {...}
        }

    Both nested dicts are marked as JSON because their schemas vary by
    type and pynetbox would otherwise wrap them in generic Records that
    swallow the unfamiliar keys.
    """

    custom_object_type = JsonField
    object = JsonField


class _Models:
    """Models namespace for the custom-objects extension.

    Explicit attributes cover the three statically known endpoints. The
    `__getattr__` fallback returns `CustomObject` for any other name so
    that dynamic per-type endpoints (e.g.
    ``nb.plugins.custom_objects.cidr_list``) deserialize into typed
    records without each Custom Object Type having to be pre-registered.

    A bare class with `__getattr__` would not work — `getattr(cls, name)`
    only consults the metaclass's `__getattr__`, not the class's own.
    Using an instance puts the fallback on the right code path.
    """

    CustomObjectTypes = CustomObjectTypes
    CustomObjectTypeFields = CustomObjectTypeFields
    LinkedObjects = LinkedObjects

    def __getattr__(self, name):
        return CustomObject


def schema_preview(api, schema_document):
    """Preview the diff a `schema_document` would produce.

    POSTs the document to ``/plugins/custom-objects/schema/preview/``
    and returns the server's diff response (a dict with a ``diffs`` key).
    No DB changes are made.

    ## Parameters

    * **api** (Api): The pynetbox client instance.
    * **schema_document** (dict): A COT schema document conforming to
        the plugin's ``cot_schema_v1.json``.

    ## Returns
    dict: The diff response.

    ## Raises
    `RequestError`: 400 if the document fails JSON Schema validation.
    """
    return _plugin_request(api, "schema/preview/").post(schema_document)


def schema_apply(api, schema_document, allow_destructive=False):
    """Apply a `schema_document` against the live DB.

    POSTs ``{"schema": schema_document, "allow_destructive": ...}`` to
    ``/plugins/custom-objects/schema/apply/`` and returns the server's
    response (``{"applied": True, "diffs": [...]}``).

    ## Parameters

    * **api** (Api): The pynetbox client instance.
    * **schema_document** (dict): A COT schema document.
    * **allow_destructive** (bool): Permit ``REMOVE`` field operations
        that drop DB columns. Defaults to ``False``.

    ## Returns
    dict: The apply response.

    ## Raises
    `RequestError`: 409 when the document contains destructive changes
    and ``allow_destructive`` is False; 400 for circular dependencies,
    unresolvable references, or invalid schema; 403 if the user lacks
    the required CustomObjectType permissions.
    """
    payload = {"schema": schema_document, "allow_destructive": allow_destructive}
    return _plugin_request(api, "schema/apply/").post(payload)


class CustomObjectsExtension(Extension):
    """pynetbox extension for the netbox-custom-objects plugin.

    Register with:

    ```python
    import pynetbox
    from pynetbox.extensions import CustomObjectsExtension

    nb = pynetbox.api(url, token="...", extensions=[CustomObjectsExtension])
    ```

    See the module docstring for usage examples.
    """

    plugin_name = "custom_objects"
    models = _Models()
    content_types = {
        "netbox_custom_objects.customobjecttype": CustomObjectTypes,
        "netbox_custom_objects.customobjecttypefield": CustomObjectTypeFields,
    }
