import unittest
from unittest.mock import Mock, patch

import pynetbox
from pynetbox.core.endpoint import DetailEndpoint, Endpoint
from pynetbox.core.extension import Extension
from pynetbox.core.response import JsonField, Record


# Models used by the extensions defined below. Modeled after the shapes
# called out in netbox-community/pynetbox#710 and #745 #751.


class Branches(Record):
    """Plugin Record subclass with a custom DetailEndpoint, like #710."""

    @property
    def merge(self):
        return DetailEndpoint(self, "merge")


class BranchingModels:
    Branches = Branches


class BranchingExtension(Extension):
    plugin_name = "branching"
    models = BranchingModels


class CustomObjectTypeFields(Record):
    """Plugin Record marking a dict field as JSON, like #751."""

    related_object_filter = JsonField


class CustomObjectsModels:
    CustomObjectTypeFields = CustomObjectTypeFields


class CustomObjectsExtension(Extension):
    plugin_name = "custom_objects"
    models = CustomObjectsModels
    content_types = {
        "custom_objects.customobjecttypefield": CustomObjectTypeFields,
    }


class ExtensionRegistrationTestCase(unittest.TestCase):
    def test_extension_registry_built(self):
        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[BranchingExtension, CustomObjectsExtension],
        )
        self.assertIn("branching", nb._extensions)
        self.assertIn("custom_objects", nb._extensions)

    def test_missing_plugin_name_raises(self):
        class BadExtension:
            models = None

        with self.assertRaises(ValueError):
            pynetbox.api(
                "http://localhost:8000", token="abc", extensions=[BadExtension]
            )

    def test_content_types_merged_into_mapper(self):
        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[CustomObjectsExtension],
        )
        self.assertIs(
            nb._content_type_mapper["custom_objects.customobjecttypefield"],
            CustomObjectTypeFields,
        )
        # Reverse mapping is rebuilt as well.
        self.assertEqual(
            nb._type_content_mapper[CustomObjectTypeFields],
            "custom_objects.customobjecttypefield",
        )
        # Built-in mappings are preserved.
        self.assertIn("dcim.cable", nb._content_type_mapper)


class PluginEndpointResolutionTestCase(unittest.TestCase):
    def test_plugin_endpoint_uses_extension_record(self):
        """An endpoint under nb.plugins.<name> resolves to the extension's Record."""
        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[BranchingExtension],
        )
        endpoint = nb.plugins.branching.branches
        self.assertIs(endpoint.return_obj, Branches)

    def test_plugin_without_extension_falls_back_to_record(self):
        nb = pynetbox.api("http://localhost:8000", token="abc")
        endpoint = nb.plugins.unknown_plugin.things
        self.assertIs(endpoint.return_obj, Record)

    def test_plugin_endpoint_with_dashed_slug(self):
        """Extension plugin_name 'custom_objects' matches URL slug 'custom-objects'."""
        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[CustomObjectsExtension],
        )
        endpoint = nb.plugins.custom_objects.custom_object_type_fields
        self.assertIs(endpoint.return_obj, CustomObjectTypeFields)
        # URL slug should still use dashes per existing convention.
        self.assertEqual(
            endpoint.url,
            "http://localhost:8000/api/plugins/custom-objects/custom-object-type-fields",
        )


class PluginRecordBehaviorTestCase(unittest.TestCase):
    def test_detail_endpoint_on_plugin_record(self):
        """#710 shape: plugin Record exposes DetailEndpoint via @property."""
        with patch("pynetbox.core.query.Request._make_call") as mock:
            mock.return_value = [{"id": 1, "name": "feature-branch"}]
            nb = pynetbox.api(
                "http://localhost:8000",
                token="abc",
                extensions=[BranchingExtension],
            )
            branch = nb.plugins.branching.branches.get(1)
            self.assertIsInstance(branch, Branches)
            self.assertIsInstance(branch.merge, DetailEndpoint)
            self.assertTrue(branch.merge.url.endswith("/branches/1/merge/"))

    def test_jsonfield_preserves_dict_on_plugin_record(self):
        """#751 shape: a JSON dict field on a plugin record stays a dict."""
        payload = {
            "id": 3,
            "name": "cidr_list",
            "related_object_filter": {
                "vrf__n": "null",
                "tenant_group": "aws-accounts",
                "mask_length__lte": 28,
            },
        }
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[payload]
        ):
            nb = pynetbox.api(
                "http://localhost:8000",
                token="abc",
                extensions=[CustomObjectsExtension],
            )
            field = nb.plugins.custom_objects.custom_object_type_fields.get(3)
            self.assertIsInstance(field, CustomObjectTypeFields)
            self.assertEqual(
                field.related_object_filter,
                {
                    "vrf__n": "null",
                    "tenant_group": "aws-accounts",
                    "mask_length__lte": 28,
                },
            )
            # And round-trips through serialize().
            self.assertEqual(
                field.serialize()["related_object_filter"],
                {
                    "vrf__n": "null",
                    "tenant_group": "aws-accounts",
                    "mask_length__lte": 28,
                },
            )


class PluginAppPickleTestCase(unittest.TestCase):
    def test_plugin_app_setstate_restores_model(self):
        """App.__setstate__ should re-resolve the extension's models on unpickle."""
        import pickle

        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[BranchingExtension],
        )
        app = nb.plugins.branching
        round_tripped = pickle.loads(pickle.dumps(app))
        # After unpickle, the model should still resolve to BranchingModels
        # because _setmodel re-consults the api's extension registry.
        self.assertIs(round_tripped.model, BranchingModels)


class GenericListExtensionTestCase(unittest.TestCase):
    def test_extension_record_used_for_gfk(self):
        """A polymorphic list item with a plugin content_type uses the extension Record."""
        nb = pynetbox.api(
            "http://localhost:8000",
            token="abc",
            extensions=[CustomObjectsExtension],
        )
        record = Record(
            {
                "id": 1,
                "things": [
                    {
                        "object_type": "custom_objects.customobjecttypefield",
                        "object": {"id": 9, "name": "cidr_list"},
                    }
                ],
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertIsInstance(record.things[0].object, CustomObjectTypeFields)
