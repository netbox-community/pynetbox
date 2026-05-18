"""Unit tests for `pynetbox.extensions.custom_objects`.

Covers the issue called out in #751 (``related_object_filter`` round-trips
as a dict) as well as the dynamic per-type endpoint resolution and the
plugin-level `schema_preview` / `schema_apply` helpers.
"""

import unittest
from unittest.mock import Mock, patch

import pynetbox
from pynetbox.core.endpoint import Endpoint
from pynetbox.core.response import Record
from pynetbox.extensions import CustomObjectsExtension
from pynetbox.extensions.custom_objects import (
    CustomObject,
    CustomObjectTypeFields,
    CustomObjectTypes,
    LinkedObjects,
    schema_apply,
    schema_preview,
)


def _api(**kwargs):
    kwargs.setdefault("extensions", [CustomObjectsExtension])
    return pynetbox.api("http://localhost:8000", token="abc", **kwargs)


class EndpointResolutionTestCase(unittest.TestCase):
    """Static endpoint names resolve to the shipped Record subclasses."""

    def setUp(self):
        self.nb = _api()

    def test_custom_object_types_resolves(self):
        endpoint = self.nb.plugins.custom_objects.custom_object_types
        self.assertIs(endpoint.return_obj, CustomObjectTypes)
        self.assertTrue(
            endpoint.url.endswith("/plugins/custom-objects/custom-object-types")
        )

    def test_custom_object_type_fields_resolves(self):
        endpoint = self.nb.plugins.custom_objects.custom_object_type_fields
        self.assertIs(endpoint.return_obj, CustomObjectTypeFields)

    def test_linked_objects_resolves(self):
        endpoint = self.nb.plugins.custom_objects.linked_objects
        self.assertIs(endpoint.return_obj, LinkedObjects)

    def test_unknown_endpoint_falls_back_to_custom_object(self):
        """Per-type endpoints aren't registered statically — they should
        resolve to ``CustomObject`` via the namespace's ``__getattr__``."""
        endpoint = self.nb.plugins.custom_objects.cidr_list
        self.assertIs(endpoint.return_obj, CustomObject)
        self.assertTrue(endpoint.url.endswith("/plugins/custom-objects/cidr-list"))


class RelatedObjectFilterRoundTripTestCase(unittest.TestCase):
    """Issue #751: ``related_object_filter`` should round-trip as a dict."""

    PAYLOAD = {
        "id": 3,
        "name": "cidr_list",
        "label": "CIDR List",
        "custom_object_type": 1,
        "type": "multiobject",
        "related_object_type": {"id": 84, "app_label": "ipam", "model": "prefix"},
        "related_object_filter": {
            "vrf__n": "null",
            "tenant_group": "aws-accounts",
            "mask_length__lte": 28,
        },
    }

    def test_get_preserves_dict(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[self.PAYLOAD]
        ):
            nb = _api()
            field = nb.plugins.custom_objects.custom_object_type_fields.get(3)

        self.assertIsInstance(field, CustomObjectTypeFields)
        self.assertEqual(field.related_object_filter, self.PAYLOAD["related_object_filter"])

    def test_serialize_preserves_dict(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[self.PAYLOAD]
        ):
            nb = _api()
            field = nb.plugins.custom_objects.custom_object_type_fields.get(3)

        # The plain serialize() output is what the user inspects (per the
        # bug report) and is also what the diffing layer uses to compute
        # updates() — both need to see the original dict.
        self.assertEqual(
            field.serialize()["related_object_filter"],
            self.PAYLOAD["related_object_filter"],
        )

    def test_related_object_type_is_preserved_dict(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[self.PAYLOAD]
        ):
            nb = _api()
            field = nb.plugins.custom_objects.custom_object_type_fields.get(3)

        self.assertEqual(
            field.related_object_type, self.PAYLOAD["related_object_type"]
        )


class CustomObjectTypeRecordTestCase(unittest.TestCase):
    """`schema_document` and `fields` nesting on a CustomObjectType."""

    def test_schema_document_preserved_as_dict(self):
        payload = {
            "id": 1,
            "name": "demo",
            "slug": "demo",
            "schema_document": {
                "schema_version": "1",
                "types": [{"slug": "demo"}],
            },
            "fields": [],
        }
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[payload]
        ):
            nb = _api()
            cot = nb.plugins.custom_objects.custom_object_types.get(1)

        self.assertIsInstance(cot, CustomObjectTypes)
        self.assertEqual(cot.schema_document, payload["schema_document"])

    def test_nested_fields_become_typed_records(self):
        """Nested `fields` list items deserialize as CustomObjectTypeFields,
        so their JSON-marked columns (e.g. related_object_filter) survive
        a nested fetch the same way they do on the dedicated endpoint."""
        payload = {
            "id": 1,
            "name": "demo",
            "fields": [
                {
                    "id": 3,
                    "name": "cidr_list",
                    "related_object_filter": {"vrf__n": "null"},
                }
            ],
        }
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[payload]
        ):
            nb = _api()
            cot = nb.plugins.custom_objects.custom_object_types.get(1)

        self.assertEqual(len(cot.fields), 1)
        nested = cot.fields[0]
        self.assertIsInstance(nested, CustomObjectTypeFields)
        self.assertEqual(nested.related_object_filter, {"vrf__n": "null"})


class CustomObjectRecordTestCase(unittest.TestCase):
    def test_dynamic_endpoint_returns_custom_object(self):
        payload = {
            "id": 7,
            "url": "http://localhost:8000/api/plugins/custom-objects/cidr-list/7/",
            "display": "thing",
            "custom_object_type": {"id": 1, "slug": "cidr-list", "name": "CIDR List"},
        }
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[payload]
        ):
            nb = _api()
            obj = nb.plugins.custom_objects.cidr_list.get(7)

        self.assertIsInstance(obj, CustomObject)
        self.assertIsInstance(obj.custom_object_type, CustomObjectTypes)
        self.assertEqual(obj.custom_object_type.slug, "cidr-list")


class LinkedObjectsTestCase(unittest.TestCase):
    """The linked-objects endpoint paginates like a normal NetBox list."""

    def test_filter_returns_linked_objects_records(self):
        item = {
            "custom_object_type": {"id": 1, "name": "T", "slug": "t"},
            "field_name": "device",
            "object": {"id": 5, "display": "thing", "name": "thing"},
        }
        # The view returns {"count": N, "results": [...]} like a normal paginated list.
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"count": 1, "next": None, "previous": None, "results": [item]},
        ):
            nb = _api()
            results = list(
                nb.plugins.custom_objects.linked_objects.filter(
                    object_type="dcim.device", object_id=5
                )
            )

        self.assertEqual(len(results), 1)
        record = results[0]
        self.assertIsInstance(record, LinkedObjects)
        # Nested fields stayed plain dicts rather than being recursed into.
        self.assertEqual(record.custom_object_type, item["custom_object_type"])
        self.assertEqual(record.object, item["object"])


class ContentTypeMappingTestCase(unittest.TestCase):
    def test_content_types_registered(self):
        nb = _api()
        self.assertIs(
            nb._content_type_mapper["netbox_custom_objects.customobjecttype"],
            CustomObjectTypes,
        )
        self.assertIs(
            nb._content_type_mapper["netbox_custom_objects.customobjecttypefield"],
            CustomObjectTypeFields,
        )

    def test_polymorphic_resolution_uses_extension_record(self):
        """A generic-FK list item whose ``object_type`` matches one of the
        extension's content types deserializes into the extension's
        Record subclass."""
        nb = _api()
        record = Record(
            {
                "id": 1,
                "items": [
                    {
                        "object_type": "netbox_custom_objects.customobjecttypefield",
                        "object": {"id": 9, "name": "cidr_list"},
                    }
                ],
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertIsInstance(record.items[0].object, CustomObjectTypeFields)


class SchemaHelpersTestCase(unittest.TestCase):
    """`schema_preview` and `schema_apply` POST to the right URL."""

    SCHEMA = {"schema_version": "1", "types": [{"slug": "demo"}]}

    def test_schema_preview_posts_document(self):
        nb = _api()
        sentinel = {"diffs": []}
        with patch(
            "pynetbox.core.query.Request.post", return_value=sentinel
        ) as mock_post:
            result = schema_preview(nb, self.SCHEMA)

        self.assertIs(result, sentinel)
        mock_post.assert_called_once_with(self.SCHEMA)

    def test_schema_apply_wraps_payload(self):
        nb = _api()
        sentinel = {"applied": True, "diffs": []}
        with patch(
            "pynetbox.core.query.Request.post", return_value=sentinel
        ) as mock_post:
            result = schema_apply(nb, self.SCHEMA, allow_destructive=True)

        self.assertIs(result, sentinel)
        mock_post.assert_called_once_with(
            {"schema": self.SCHEMA, "allow_destructive": True}
        )

    def test_schema_apply_defaults_allow_destructive_false(self):
        nb = _api()
        with patch(
            "pynetbox.core.query.Request.post", return_value={}
        ) as mock_post:
            schema_apply(nb, self.SCHEMA)

        payload = mock_post.call_args.args[0]
        self.assertFalse(payload["allow_destructive"])

    def test_schema_helpers_target_plugin_url(self):
        """Sanity-check the URL the helper builds — easy to break, easy to forget."""
        nb = _api()
        captured = {}

        def fake_request(base, **kwargs):
            captured.setdefault("bases", []).append(base)
            return Mock(post=Mock(return_value={}))

        with patch("pynetbox.extensions.custom_objects.Request", new=fake_request):
            schema_preview(nb, self.SCHEMA)
            schema_apply(nb, self.SCHEMA)

        self.assertEqual(
            captured["bases"],
            [
                "http://localhost:8000/api/plugins/custom-objects/schema/preview/",
                "http://localhost:8000/api/plugins/custom-objects/schema/apply/",
            ],
        )


if __name__ == "__main__":
    unittest.main()
