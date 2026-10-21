import copy
import pickle
import unittest
from unittest.mock import Mock, patch

from pynetbox.core.endpoint import Endpoint
from pynetbox.core.response import JsonField, Record, RecordSet, flatten_custom
from pynetbox.extensions.custom_objects import CustomObject
from pynetbox.models.dcim import Devices, DeviceTypes, FrontPorts
from pynetbox.models.ipam import IpAddresses
from pynetbox.models.users import Permissions, Users


class FlattenCustomTest(unittest.TestCase):
    def test_flatten_custom(self):
        test_dicts = [
            {"foo0": []},
            {"foo1": [{"a": "b"}]},
            {"foo2": [{"a": "b", "c": "d"}]},
            {"foo3": 123},
            {"foo4": "a"},
            {"foo5": {"a": "b"}},
            {"foo6": [{"a": "b", "c": "d"}]},
        ]
        for test_dict in test_dicts:
            ret = flatten_custom(test_dict)
            assert ret == test_dict

    def test_flatten_custom_selection_values(self):
        """NetBox 4.7+ returns selection values as {value, label} (#806)."""
        ret = flatten_custom(
            {
                "select": {"value": "a", "label": "A"},
                "multiselect": [
                    {"value": "a", "label": "A"},
                    {"value": "b", "label": "B"},
                ],
                "mixed": [{"value": "a", "label": "A"}, "b"],
            }
        )
        self.assertEqual(ret, {"select": "a", "multiselect": ["a", "b"], "mixed": ["a", "b"]})

    def test_flatten_custom_raw_selection_values(self):
        """Selection values from NetBox < 4.7 are raw and pass through."""
        test_dict = {"select": "a", "multiselect": ["a", "b"]}
        self.assertEqual(flatten_custom(test_dict), test_dict)

    def test_flatten_custom_object_values(self):
        ret = flatten_custom(
            {
                "object": {"id": 3, "url": "http://localhost:8000/api/dcim/sites/3/"},
                "multiobject": [{"id": 3}, {"id": 4}],
            }
        )
        self.assertEqual(ret, {"object": 3, "multiobject": [3, 4]})


class RecordTestCase(unittest.TestCase):
    def test_attribute_access(self):
        test_values = {
            "id": 123,
            "units": 12,
            "nested_dict": {"id": 222, "name": "bar"},
            "int_list": [123, 321, 231],
        }
        test_obj = Record(test_values, None, None)
        self.assertEqual(test_obj.id, 123)
        self.assertEqual(test_obj.units, 12)
        self.assertEqual(test_obj.nested_dict.name, "bar")
        self.assertEqual(test_obj.int_list[1], 321)
        with self.assertRaises(AttributeError) as _:
            test_obj.nothing

    def test_dunder_attribute_does_not_trigger_full_details(self):
        """Probing for a missing dunder attribute (e.g. pydantic's
        isinstance check, copy/pickle machinery) must not fire a network
        request nor clobber local modifications. See issue #688.
        """
        test_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": "original",
        }
        test_obj = Record(test_values, Mock(base_url="http://localhost:8000/api"), None)
        test_obj.name = "modified"
        with patch.object(Record, "full_details") as full_details:
            # Simulate what the real full_details would do if reached:
            # re-parse the server values and overwrite local edits.
            def clobber():
                test_obj.name = "original"
                return True

            full_details.side_effect = clobber

            self.assertFalse(hasattr(test_obj, "__pydantic_decorators__"))
            full_details.assert_not_called()
        # Local modification is preserved: the dunder guard short-circuited
        # before full_details could run and clobber it.
        self.assertEqual(test_obj.name, "modified")

    def test_full_details_preserves_local_edits(self):
        """Re-fetching a record must not discard pending local changes.

        Reading a missing attribute (here via str(), which looks for
        `label`) hydrates the record. That used to refresh the diff
        baseline, so the edit below looked already-saved and save()
        sent nothing. See issue #808.
        """
        server_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "display": "DEVICE_TYPE (123)",
            "custom_fields": {"my_field": "old"},
        }
        test_obj = Record(
            copy.deepcopy(server_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )
        test_obj.custom_fields["my_field"] = "new"

        # str() misses on `label` and hydrates. Deep-copy the payload: a
        # shallow one shares the nested custom_fields dict with the record.
        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(server_values)]),
        ):
            self.assertEqual(str(test_obj), "DEVICE_TYPE (123)")

        self.assertEqual(test_obj.custom_fields, {"my_field": "new"})
        self.assertEqual(
            test_obj.updates(), {"custom_fields": {"my_field": "new"}}
        )

    def test_full_details_preserves_local_scalar_edit(self):
        """The custom_fields case above goes through the JsonField path.
        A plain scalar takes a different branch of _parse_values, so cover
        it too. See issue #808.
        """
        server_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "OLD",
        }
        test_obj = Record(
            copy.deepcopy(server_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )
        test_obj.serial = "NEW"

        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(server_values)]),
        ):
            test_obj.full_details()

        self.assertEqual(test_obj.serial, "NEW")
        self.assertEqual(test_obj.updates(), {"serial": "NEW"})

    def test_full_details_refreshes_untouched_fields(self):
        """Preserving local edits must not stop untouched fields from
        picking up fresh server state. See issue #808.
        """
        init_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "OLD",
            "custom_fields": {"my_field": "old"},
        }
        test_obj = Record(
            copy.deepcopy(init_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )
        test_obj.custom_fields["my_field"] = "new"

        # The server has moved `serial` on, a field nobody edited locally.
        server_values = dict(copy.deepcopy(init_values), serial="SERVER")
        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(server_values)]),
        ):
            test_obj.full_details()

        self.assertEqual(test_obj.serial, "SERVER")
        # Only the locally-edited field is pending; `serial` matches the
        # server, so it must not show up as a change to send back.
        self.assertEqual(
            test_obj.updates(), {"custom_fields": {"my_field": "new"}}
        )

    def test_full_details_clean_record_stays_clean(self):
        """Hydrating a record with no local edits produces no diff.
        See issue #808.
        """
        server_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "OLD",
            "custom_fields": {"my_field": "old"},
        }
        test_obj = Record(
            copy.deepcopy(server_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )

        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(server_values)]),
        ):
            test_obj.full_details()

        self.assertEqual(test_obj.updates(), {})

    def assertOneBaselineEntryPerField(self, record, payload):
        # Compare counts first. A growing cache then fails with a short count
        # mismatch, not a long list diff.
        self.assertEqual(len(record._init_cache), len(payload))
        self.assertEqual(list(record._init_cache), list(payload))

    def test_full_details_repeated_keeps_one_baseline_entry_per_field(self):
        """full_details() re-parses the record. Each re-parse must replace
        change baseline entries, not add new ones (#813).
        """
        server_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "OLD",
            "custom_fields": {"my_field": "old"},
        }
        test_obj = Record(
            copy.deepcopy(server_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )

        with patch(
            "pynetbox.core.query.Request.get",
            side_effect=lambda *a, **k: iter([copy.deepcopy(server_values)]),
        ):
            for _ in range(3):
                test_obj.full_details()

        self.assertOneBaselineEntryPerField(test_obj, server_values)

    def test_save_repeated_keeps_one_baseline_entry_per_field(self):
        """save() re-parses the PATCH response (#731). Each re-parse must
        replace change baseline entries, not add new ones (#813).
        """
        api = Mock(token="abc123", base_url="http://localhost:8000/api")
        server_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "0",
        }
        test_obj = Record(copy.deepcopy(server_values), api, None)
        api.http_session.patch.return_value.ok = True

        for i in range(1, 4):
            test_obj.serial = str(i)
            server_values["serial"] = str(i)
            api.http_session.patch.return_value.json.return_value = copy.deepcopy(
                server_values
            )
            self.assertTrue(test_obj.save())

        self.assertOneBaselineEntryPerField(test_obj, server_values)
        self.assertEqual(test_obj._init_cache["serial"], "3")

    def test_full_details_dirty_field_keeps_old_baseline_single_entry(self):
        """full_details() puts back the old change baseline of an edited
        field (#808). That write must replace the server value, not add a
        second entry (#813).
        """
        init_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": None,
            "serial": "OLD",
        }
        test_obj = Record(
            copy.deepcopy(init_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )
        test_obj.serial = "NEW"

        server_values = dict(init_values, serial="SERVER")
        with patch(
            "pynetbox.core.query.Request.get",
            side_effect=lambda *a, **k: iter([copy.deepcopy(server_values)]),
        ):
            test_obj.full_details()

        self.assertOneBaselineEntryPerField(test_obj, init_values)
        self.assertEqual(test_obj._init_cache["serial"], "OLD")
        self.assertEqual(test_obj.updates(), {"serial": "NEW"})

    def test_refetch_preserves_serialize_key_order(self):
        """serialize() must keep the original key order when a re-fetch
        returns fields in a different order (#813).
        """
        init_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": "dev1",
            "serial": "OLD",
            "asset_tag": None,
        }
        test_obj = Record(
            copy.deepcopy(init_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )

        server_values = {
            "asset_tag": None,
            "serial": "SERVER",
            "name": "dev1",
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "id": 123,
        }
        with patch(
            "pynetbox.core.query.Request.get",
            side_effect=lambda *a, **k: iter([copy.deepcopy(server_values)]),
        ):
            test_obj.full_details()

        self.assertEqual(list(test_obj.serialize()), list(init_values))
        self.assertEqual(list(test_obj.serialize(init=True)), list(init_values))
        self.assertEqual(test_obj._diff(), set())

    def test_iter_survives_hydration_mid_loop(self):
        """Hydration inside a loop over the record adds keys to the change
        baseline. A loop over the live dict then raises RuntimeError (#813).
        """
        brief_values = {
            "id": 123,
            "url": "http://localhost:8000/api/dcim/devices/123/",
            "name": "dev1",
        }
        full_values = dict(brief_values, serial="ABC", asset_tag=None)
        test_obj = Record(
            copy.deepcopy(brief_values),
            Mock(base_url="http://localhost:8000/api"),
            None,
        )

        with patch(
            "pynetbox.core.query.Request.get",
            side_effect=lambda *a, **k: iter([copy.deepcopy(full_values)]),
        ):
            keys = []
            for k, _ in test_obj:
                keys.append(k)
                test_obj.full_details()

        self.assertEqual(keys, list(brief_values))
        self.assertEqual(dict(test_obj)["serial"], "ABC")

    def test_pickle_round_trip_preserves_change_baseline(self):
        """Callers pickle records for multiprocessing (#152, #459). The
        change baseline must survive pickling, or pending edits disappear.
        """
        import pickle

        import pynetbox

        nb = pynetbox.api("http://localhost:8000", token="abc")
        test_obj = Record(
            {
                "id": 123,
                "url": "http://localhost:8000/api/dcim/devices/123/",
                "name": "dev1",
                "serial": "OLD",
                "site": {
                    "id": 1,
                    "url": "http://localhost:8000/api/dcim/sites/1/",
                    "name": "site1",
                },
            },
            nb,
            None,
        )
        test_obj.serial = "NEW"

        round_tripped = pickle.loads(pickle.dumps(test_obj))

        self.assertEqual(round_tripped.updates(), {"serial": "NEW"})
        self.assertEqual(round_tripped.updates(), test_obj.updates())
        self.assertEqual(round_tripped.serialize(), test_obj.serialize())
        self.assertEqual(dict(round_tripped), dict(test_obj))

    def test_dict_access(self):
        test_values = {
            "id": 123,
            "units": 12,
            "nested_dict": {"id": 222, "name": "bar"},
            "int_list": [123, 321, 231],
        }
        test_obj = Record(test_values, None, None)
        self.assertEqual(test_obj["id"], 123)
        self.assertEqual(test_obj["units"], 12)
        self.assertEqual(test_obj["nested_dict"]["name"], "bar")
        self.assertEqual(test_obj["int_list"][1], 321)
        with self.assertRaises(KeyError) as _:
            test_obj["nothing"]

    def test_nested_dict_key_collides_with_record_method(self):
        # Regression for issue #749: a nested dict key like "updates"
        # collided with Record.updates and was invoked as a constructor.
        test_values = {
            "id": 1,
            "config_context": {"router_bgp": {"updates": {"wait_install": True}}},
        }
        test_obj = Record(test_values, Mock(base_url="http://test"), None)
        self.assertEqual(
            test_obj.config_context.router_bgp.updates.wait_install, True
        )

    def test_serialize_list_of_records(self):
        test_values = {
            "id": 123,
            "tagged_vlans": [
                {
                    "id": 1,
                    "url": "http://localhost:8000/api/ipam/vlans/1/",
                    "vid": 1,
                    "name": "test1",
                    "display_name": "test1",
                },
                {
                    "id": 2,
                    "url": "http://localhost:8000/api/ipam/vlans/2/",
                    "vid": 2,
                    "name": "test 2",
                    "display_name": "test2",
                },
            ],
        }
        test_obj = Record(test_values, Mock(base_url="test"), None)
        test = test_obj.serialize()
        self.assertEqual(test["tagged_vlans"], [1, 2])

    def test_serialize_list_of_ints(self):
        test_values = {"id": 123, "units": [12]}
        test_obj = Record(test_values, None, None)
        test = test_obj.serialize()
        self.assertEqual(test["units"], [12])

    def test_serialize_string_tag_set(self):
        test_values = {"id": 123, "tags": ["foo", "bar", "foo"]}
        test = Record(test_values, None, None).serialize()
        self.assertEqual(len(test["tags"]), 2)

    def test_serialize_dict_tag_set(self):
        test_values = {
            "id": 123,
            "tags": [
                {
                    "id": 1,
                    "name": "foo",
                },
                {
                    "id": 2,
                    "name": "bar",
                },
                {
                    "id": 3,
                    "name": "baz",
                },
            ],
        }
        test = Record(test_values, None, None).serialize()
        self.assertEqual(len(test["tags"]), 3)

    def test_diff(self):
        test_values = {
            "id": 123,
            "custom_fields": {"foo": "bar"},
            "string_field": "foobar",
            "int_field": 1,
            "nested_dict": {"id": 222, "name": "bar"},
            "tags": ["foo", "bar"],
            "int_list": [123, 321, 231],
            "local_context_data": {"data": ["one"]},
        }
        test = Record(test_values, None, None)
        test.tags.append("baz")
        test.nested_dict = 1
        test.string_field = "foobaz"
        test.local_context_data["data"].append("two")
        self.assertEqual(
            test._diff(), {"tags", "nested_dict", "string_field", "local_context_data"}
        )

    def test_diff_append_records_list(self):
        test_values = {
            "id": 123,
            "tagged_vlans": [
                {
                    "id": 1,
                    "url": "http://localhost:8000/api/ipam/vlans/1/",
                    "vid": 1,
                    "name": "test1",
                    "display_name": "test1",
                }
            ],
        }
        test_obj = Record(test_values, Mock(base_url="test"), None)
        test_obj.tagged_vlans.append(1)
        test = test_obj._diff()
        self.assertFalse(test)

    def test_serialize_list_of_records_without_id(self):
        # NetBox 4.5+ FrontPort.rear_ports mapping items have no id.
        # Regression test for issue #745.
        test_values = {
            "id": 123,
            "rear_ports": [
                {"position": 1, "rear_port": 1653, "rear_port_position": 1},
                {"position": 2, "rear_port": 1654, "rear_port_position": 1},
            ],
        }
        test_obj = Record(test_values, Mock(base_url="test"), None)
        result = test_obj.serialize()
        self.assertEqual(result["rear_ports"], test_values["rear_ports"])

    def test_diff_unchanged_list_of_records_without_id(self):
        # Regression test for issue #745: no false-positive diff for
        # untouched mapping lists like FrontPort.rear_ports.
        test_values = {
            "id": 123,
            "rear_ports": [
                {"position": 1, "rear_port": 1653, "rear_port_position": 1},
            ],
        }
        test_obj = Record(test_values, Mock(base_url="test"), None)
        self.assertFalse(test_obj._diff())

    def test_diff_detects_changed_idless_nested_record(self):
        test_obj = Record(
            {
                "id": 123,
                "rear_ports": [
                    {"position": 1, "rear_port": 1653, "rear_port_position": 1},
                ],
            },
            Mock(base_url="test"),
            None,
        )

        test_obj.rear_ports[0].position = 2

        self.assertEqual(test_obj._diff(), {"rear_ports"})

    def test_json_field_list_of_dicts_kept_raw(self):
        # Regression test for issue #625: a column explicitly marked
        # JsonField that holds a list of dicts (e.g. an arbitrary plugin
        # JSON field) must stay as plain dicts, not be coerced into nested
        # Records. Coercion broke serialize()/save() because the dicts have
        # no id.
        from pynetbox.core.response import JsonField

        class PluginRecord(Record):
            my_json_list = JsonField

        test_values = {
            "id": 123,
            "my_json_list": [{"example": "bug"}, {"another": "value"}],
        }
        test_obj = PluginRecord(test_values, Mock(base_url="test"), None)

        # Items remain plain dicts, not Records.
        self.assertIsInstance(test_obj.my_json_list[0], dict)
        self.assertEqual(test_obj.my_json_list, test_values["my_json_list"])

        # serialize() round-trips the raw JSON and save() doesn't choke.
        self.assertEqual(
            test_obj.serialize()["my_json_list"], test_values["my_json_list"]
        )
        # Unchanged list produces no false-positive diff.
        self.assertFalse(test_obj._diff())

    def test_dict(self):
        test_values = {
            "id": 123,
            "custom_fields": {"foo": "bar"},
            "string_field": "foobar",
            "int_field": 1,
            "nested_dict": {"id": 222, "name": "bar"},
            "tags": ["foo", "bar"],
            "int_list": [123, 321, 231],
            "empty_list": [],
            "record_list": [
                {
                    "id": 123,
                    "name": "Test",
                    "str_attr": "foo",
                    "int_attr": 123,
                    "custom_fields": {"foo": "bar"},
                    "tags": ["foo", "bar"],
                },
                {
                    "id": 321,
                    "name": "Test 1",
                    "str_attr": "bar",
                    "int_attr": 321,
                    "custom_fields": {"foo": "bar"},
                    "tags": ["foo", "bar"],
                },
            ],
        }
        test = Record(test_values, None, None)
        self.assertEqual(dict(test), test_values)

    def test_choices_idempotence(self):
        test_values = {
            "id": 123,
            "choices_test": {
                "value": "test",
                "label": "test",
            },
        }
        test = Record(test_values, None, None)
        test.choices_test = "test"
        self.assertFalse(test._diff())

    def test_hash(self):
        endpoint = Mock()
        endpoint.name = "test-endpoint"
        test = Record({}, None, endpoint)
        self.assertIsInstance(hash(test), int)

    def test_hash_diff(self):
        endpoint1 = Mock()
        endpoint1.name = "test-endpoint"
        endpoint2 = Mock()
        endpoint2.name = "test-endpoint"
        test1 = Record({}, None, endpoint1)
        test1.id = 1
        test2 = Record({}, None, endpoint2)
        test2.id = 2
        self.assertNotEqual(hash(test1), hash(test2))

    def test_compare(self):
        endpoint1 = Mock()
        endpoint1.name = "test-endpoint"
        endpoint2 = Mock()
        endpoint2.name = "test-endpoint"
        test1 = Record({}, None, endpoint1)
        test1.id = 1
        test2 = Record({}, None, endpoint2)
        test2.id = 1
        self.assertEqual(test1, test2)

    def test_nested_write(self):
        app = Mock()
        app.token = "abc123"
        app.base_url = "http://localhost:8080/api"
        endpoint = Mock()
        endpoint.name = "test-endpoint"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "child": {
                    "id": 321,
                    "name": "test123",
                    "url": "http://localhost:8080/api/test-app/test-endpoint/321/",
                },
            },
            app,
            endpoint,
        )
        # Mock PATCH response - NetBox returns the updated object
        app.http_session.patch.return_value.ok = True
        app.http_session.patch.return_value.json.return_value = {
            "id": 321,
            "name": "test321",
            "url": "http://localhost:8080/api/test-app/test-endpoint/321/",
        }
        test.child.name = "test321"
        test.child.save()
        self.assertEqual(
            app.http_session.patch.call_args[0][0],
            "http://localhost:8080/api/test-app/test-endpoint/321/",
        )

    def test_nested_write_with_directory_in_base_url(self):
        app = Mock()
        app.token = "abc123"
        app.base_url = "http://localhost:8080/testing/api"
        endpoint = Mock()
        endpoint.name = "test-endpoint"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "child": {
                    "id": 321,
                    "name": "test123",
                    "url": "http://localhost:8080/testing/api/test-app/test-endpoint/321/",
                },
            },
            app,
            endpoint,
        )
        # Mock PATCH response - NetBox returns the updated object
        app.http_session.patch.return_value.ok = True
        app.http_session.patch.return_value.json.return_value = {
            "id": 321,
            "name": "test321",
            "url": "http://localhost:8080/testing/api/test-app/test-endpoint/321/",
        }
        test.child.name = "test321"
        test.child.save()
        self.assertEqual(
            app.http_session.patch.call_args[0][0],
            "http://localhost:8080/testing/api/test-app/test-endpoint/321/",
        )

    def test_endpoint_from_url(self):
        api = Mock()
        api.base_url = "http://localhost:8080/api"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "url": "http://localhost:8080/api/test-app/test-endpoint/1/",
            },
            api,
            None,
        )
        ret = test._endpoint_from_url(test.url)
        self.assertEqual(ret.name, "test-endpoint")

    def test_endpoint_from_url_with_directory_in_base_url(self):
        api = Mock()
        api.base_url = "http://localhost:8080/testing/api"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "url": "http://localhost:8080/testing/api/test-app/test-endpoint/1/",
            },
            api,
            None,
        )
        ret = test._endpoint_from_url(test.url)
        self.assertEqual(ret.name, "test-endpoint")

    def test_endpoint_from_url_with_plugins(self):
        api = Mock()
        api.base_url = "http://localhost:8080/api"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "url": "http://localhost:8080/api/plugins/test-app/test-endpoint/1/",
            },
            api,
            None,
        )
        ret = test._endpoint_from_url(test.url)
        self.assertEqual(ret.name, "test-endpoint")

    def test_endpoint_from_url_with_plugins_and_directory_in_base_url(self):
        api = Mock()
        api.base_url = "http://localhost:8080/testing/api"
        test = Record(
            {
                "id": 123,
                "name": "test",
                "url": "http://localhost:8080/testing/api/plugins/test-app/test-endpoint/1/",
            },
            api,
            None,
        )
        ret = test._endpoint_from_url(test.url)
        self.assertEqual(ret.name, "test-endpoint")

    def test_serialize_tag_list_order(self):
        """Add tests to ensure we're preserving tag order

        This test could still give false-negatives, but making the tag list
        longer helps mitigate that.
        """

        test_tags = [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
        ]
        test = Record({"id": 123, "tags": test_tags}, None, None).serialize()
        self.assertEqual(test["tags"], test_tags)

    def test_save_updates_cache(self):
        """Test that save() updates _init_cache after successful PATCH.

        This test verifies the fix for issue #586 where resetting an object
        attribute to its initial value after a save() would fail because
        _init_cache wasn't updated.
        """
        api = Mock()
        api.token = "abc123"
        api.base_url = "http://localhost:8000/api"

        endpoint = Mock()
        endpoint.url = "http://localhost:8000/api/dcim/interfaces/"
        endpoint.name = "interfaces"

        # Initial values - bridge is set to record with id=1
        initial_values = {
            "id": 415,
            "name": "eth3",
            "bridge": {"id": 1, "name": "br-native"},
            "url": "http://localhost:8000/api/dcim/interfaces/415/",
        }

        test_obj = Record(initial_values, api, endpoint)

        # First save: set bridge to None
        test_obj.bridge = None
        updates = test_obj.updates()
        self.assertEqual(updates, {"bridge": None})

        # Mock PATCH response
        api.http_session.patch.return_value.ok = True
        api.http_session.patch.return_value.json.return_value = {
            "id": 415,
            "name": "eth3",
            "bridge": None,
            "url": "http://localhost:8000/api/dcim/interfaces/415/",
        }

        # Save the change
        self.assertTrue(test_obj.save())

        # After save, _init_cache should be updated, so setting back to original
        # value should be detected as a change
        test_obj.bridge = Record({"id": 1, "name": "br-native"}, api, endpoint)
        updates = test_obj.updates()

        # This should now contain the bridge update
        self.assertEqual(updates, {"bridge": 1})

    def test_serialize_includes_new_field_set_to_none(self):
        """Regression test for issue #708: serialize() should include fields set after init."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)
        test_obj.new_field = None

        current = test_obj.serialize()
        self.assertIn("new_field", current)
        self.assertIsNone(current["new_field"])

        init = test_obj.serialize(init=True)
        self.assertNotIn("new_field", init)

    def test_serialize_includes_new_field_set_to_value(self):
        """Regression test for issue #708: serialize() should include all new fields."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)
        test_obj.new_string = "value"
        test_obj.new_int = 42
        test_obj.new_none = None

        current = test_obj.serialize()
        self.assertEqual(current["new_string"], "value")
        self.assertEqual(current["new_int"], 42)
        self.assertIsNone(current["new_none"])

        init = test_obj.serialize(init=True)
        self.assertNotIn("new_string", init)
        self.assertNotIn("new_int", init)
        self.assertNotIn("new_none", init)

    def test_diff_detects_new_field_set_to_none(self):
        """Regression test for issue #708: _diff() should detect new fields."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)
        test_obj.primary_mac_address = None

        diff = test_obj._diff()
        self.assertIn("primary_mac_address", diff)

    def test_updates_includes_new_field_set_to_none(self):
        """Regression test for issue #708: updates() should include new fields set to None."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)
        test_obj.primary_mac_address = None

        updates = test_obj.updates()
        self.assertIn("primary_mac_address", updates)
        self.assertIsNone(updates["primary_mac_address"])

    def test_updates_includes_new_field_set_to_value(self):
        """Regression test for issue #708: updates() should include all new fields."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)
        test_obj.new_field = "new_value"
        test_obj.another_field = 42

        updates = test_obj.updates()
        self.assertEqual(updates["new_field"], "new_value")
        self.assertEqual(updates["another_field"], 42)

    def test_nested_object_field_update_issue_708(self):
        """Regression test for issue #708: nested objects with limited fields."""
        api = Mock()
        api.base_url = "http://localhost:8000/api"
        interface = Record(
            {
                "id": 1,
                "name": "eth0",
                "url": "http://localhost:8000/api/dcim/interfaces/1/",
            },
            api,
            None,
        )
        interface.primary_mac_address = None

        updates = interface.updates()
        self.assertIn("primary_mac_address", updates)
        self.assertIsNone(updates["primary_mac_address"])

        diff = interface._diff()
        self.assertIn("primary_mac_address", diff)

    def test_diff_partial_custom_fields_no_false_change(self):
        """Regression test for issue #748: assigning a subset of custom_fields
        should not flag the omitted fields as changed."""
        test_obj = Record(
            {
                "id": 123,
                "name": "testsite",
                "custom_fields": {"testfield": "val", "other_field": None},
            },
            None,
            None,
        )
        # Re-assign only the field we care about, leaving its value unchanged.
        test_obj.custom_fields = {"testfield": "val"}
        self.assertFalse(test_obj._diff())

    def test_diff_partial_custom_fields_detects_real_change(self):
        """Issue #748: a changed value in a partial custom_fields assignment is
        still detected."""
        test_obj = Record(
            {
                "id": 123,
                "name": "testsite",
                "custom_fields": {"testfield": "val", "other_field": None},
            },
            None,
            None,
        )
        test_obj.custom_fields = {"testfield": "new_val"}
        self.assertEqual(test_obj._diff(), {"custom_fields"})

    def test_diff_partial_custom_fields_detects_new_key(self):
        """Issue #748: assigning a custom field key that was not in the original
        response is detected as a change."""
        test_obj = Record(
            {
                "id": 123,
                "name": "testsite",
                "custom_fields": {"testfield": "val", "other_field": None},
            },
            None,
            None,
        )
        test_obj.custom_fields = {"brand_new_key": "val"}
        self.assertEqual(test_obj._diff(), {"custom_fields"})

    def test_diff_partial_custom_fields_detects_explicit_none_clear(self):
        """Issue #748: explicitly setting a custom field to None to clear it is
        detected as a change."""
        test_obj = Record(
            {
                "id": 123,
                "name": "testsite",
                "custom_fields": {"testfield": "val", "other_field": None},
            },
            None,
            None,
        )
        test_obj.custom_fields = {"testfield": None}
        self.assertEqual(test_obj._diff(), {"custom_fields"})

    def _selection_cf_record(self):
        return Record(
            {
                "id": 123,
                "name": "testsite",
                "custom_fields": {
                    "select": {"value": "a", "label": "A"},
                    "multiselect": [
                        {"value": "a", "label": "A"},
                        {"value": "b", "label": "B"},
                    ],
                    "json": {"value": 5, "label": "five"},
                    "text": "foo",
                },
            },
            None,
            None,
        )

    def test_updates_omits_unchanged_custom_fields(self):
        """Regression test for issue #806: editing one custom field in place must
        not send the others back in the shape NetBox returned them."""
        test_obj = self._selection_cf_record()
        test_obj.custom_fields["text"] = "bar"
        self.assertEqual(test_obj.updates(), {"custom_fields": {"text": "bar"}})

    def test_updates_flattens_changed_selection_values(self):
        """A {value, label} copied into a changed custom field is sent raw."""
        test_obj = self._selection_cf_record()
        test_obj.custom_fields["select"] = {"value": "c", "label": "C"}
        self.assertEqual(test_obj.updates(), {"custom_fields": {"select": "c"}})

    def test_updates_flattens_in_place_multiselect_edit(self):
        test_obj = self._selection_cf_record()
        test_obj.custom_fields["multiselect"].append("c")
        self.assertEqual(
            test_obj.updates(), {"custom_fields": {"multiselect": ["a", "b", "c"]}}
        )

    def test_updates_same_selection_value_is_no_change(self):
        test_obj = self._selection_cf_record()
        test_obj.custom_fields["select"] = "a"
        self.assertEqual(test_obj.updates(), {})

    def test_serialize_excludes_internal_attributes(self):
        """Ensure serialize() filters out internal Record metadata."""
        test_obj = Record({"id": 123, "name": "test"}, None, None)

        serialized = test_obj.serialize()
        for attr in [
            "api",
            "endpoint",
            "url",
            "has_details",
            "default_ret",
            "_init_cache",
        ]:
            self.assertNotIn(attr, serialized)

    def test_link_peers_typed_by_sibling_content_type(self):
        """Regression for issue #519: link_peers items should be cast to the
        Record subclass identified by the sibling link_peers_type field."""
        import pynetbox
        from pynetbox.models.circuits import CircuitTerminations

        nb = pynetbox.api("http://localhost:8000", token="abc")
        record = Record(
            {
                "id": 7,
                "name": "et-0/0/0",
                "link_peers": [
                    {
                        "id": 1,
                        "url": "http://localhost:8000/api/circuits/circuit-terminations/1/",
                        "display": "Termination A",
                    }
                ],
                "link_peers_type": "circuits.circuittermination",
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertEqual(len(record.link_peers), 1)
        self.assertIsInstance(record.link_peers[0], CircuitTerminations)
        self.assertEqual(record.link_peers[0].id, 1)

    def test_connected_endpoints_typed_by_sibling_content_type(self):
        """Regression for issue #519: connected_endpoints items should be cast
        to the Record subclass identified by the sibling
        connected_endpoints_type field."""
        import pynetbox
        from pynetbox.models.dcim import Interfaces

        nb = pynetbox.api("http://localhost:8000", token="abc")
        record = Record(
            {
                "id": 7,
                "name": "et-0/0/0",
                "connected_endpoints": [
                    {
                        "id": 22,
                        "url": "http://localhost:8000/api/dcim/interfaces/22/",
                        "display": "eth0",
                        "name": "eth0",
                    }
                ],
                "connected_endpoints_type": "dcim.interface",
                "connected_endpoints_reachable": True,
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertEqual(len(record.connected_endpoints), 1)
        self.assertIsInstance(record.connected_endpoints[0], Interfaces)
        self.assertEqual(record.connected_endpoints[0].name, "eth0")

    def test_sibling_type_null_falls_back_to_default(self):
        """A null sibling type (no link peer present) should leave the empty
        list alone and not raise."""
        import pynetbox

        nb = pynetbox.api("http://localhost:8000", token="abc")
        record = Record(
            {
                "id": 7,
                "name": "et-0/0/0",
                "link_peers": [],
                "link_peers_type": None,
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertEqual(record.link_peers, [])
        self.assertIsNone(record.link_peers_type)

    def test_sibling_type_unmapped_falls_back_to_default_record(self):
        """If the sibling content type isn't in the mapper, items still
        become Records rather than raw dicts."""
        import pynetbox

        nb = pynetbox.api("http://localhost:8000", token="abc")
        record = Record(
            {
                "id": 7,
                "name": "et-0/0/0",
                "link_peers": [
                    {
                        "id": 99,
                        "url": "http://localhost:8000/api/some_plugin/some_models/99/",
                        "display": "plugin obj",
                    }
                ],
                "link_peers_type": "some_plugin.some_model",
            },
            nb,
            Mock(spec=Endpoint),
        )
        self.assertEqual(len(record.link_peers), 1)
        self.assertIsInstance(record.link_peers[0], Record)
        self.assertEqual(record.link_peers[0].id, 99)


class FieldTypeMarkerTestCase(unittest.TestCase):
    """An omitted field type marker field (e.g. `Devices.device_type`)
    must not return the marker class (#812)."""

    def test_missing_marker_field_raises(self):
        device = Devices({"id": 1, "name": "test"}, None, None)
        with self.assertRaises(AttributeError):
            device.device_type
        self.assertFalse(hasattr(device, "device_type"))

    def test_class_access_returns_marked_type(self):
        self.assertIs(Devices.device_type, DeviceTypes)
        self.assertEqual(Permissions.users, [Users])
        self.assertIs(Devices.config_context, JsonField)

    def test_missing_list_marker_field_raises(self):
        permission = Permissions({"id": 1, "name": "test"}, None, None)
        with self.assertRaises(AttributeError):
            permission.users

    def test_present_list_marker_field_builds_records(self):
        permission = Permissions(
            {"id": 1, "name": "test", "users": [{"id": 2, "username": "u"}]},
            None,
            None,
        )
        self.assertIsInstance(permission.users[0], Users)

    def test_missing_json_field_marker_raises(self):
        device = Devices({"id": 1, "name": "test"}, None, None)
        with self.assertRaises(AttributeError):
            device.config_context

    def test_present_json_field_marker_kept_raw(self):
        device = Devices(
            {"id": 1, "name": "test", "config_context": {"a": {"id": 1}}},
            None,
            None,
        )
        self.assertEqual(device.config_context, {"a": {"id": 1}})

    def test_missing_single_underscore_marker_raises(self):
        obj = CustomObject({"id": 1}, None, None)
        with self.assertRaises(AttributeError):
            obj._context

    def test_subclass_inherited_and_redeclared_markers(self):
        class InheritingDevice(Devices):
            pass

        class RedeclaringDevice(Devices):
            device_type = DeviceTypes

        for cls in (InheritingDevice, RedeclaringDevice):
            with self.subTest(cls=cls.__name__):
                self.assertIs(cls.device_type, DeviceTypes)
                with self.assertRaises(AttributeError):
                    cls({"id": 1}, None, None).device_type
                device = cls({"id": 1, "device_type": {"id": 2}}, None, None)
                self.assertIsInstance(device.device_type, DeviceTypes)

    def test_subclass_created_with_type_is_wrapped(self):
        Dynamic = type("Dynamic", (Record,), {"device_type": DeviceTypes})
        with self.assertRaises(AttributeError):
            Dynamic({"id": 1}, None, None).device_type
        device = Dynamic({"id": 1, "device_type": {"id": 2}}, None, None)
        self.assertIsInstance(device.device_type, DeviceTypes)

    def test_pickle_round_trip(self):
        device = Devices(
            {"id": 1, "name": "test", "primary_ip": {"id": 3, "address": "x"}},
            None,
            None,
        )
        # The test unpickles its own record, not untrusted data.
        restored = pickle.loads(pickle.dumps(device))
        self.assertIsInstance(restored.primary_ip, IpAddresses)
        self.assertEqual(restored.primary_ip.id, 3)
        with self.assertRaises(AttributeError):
            restored.device_type

    api = Mock(base_url="http://localhost:8000/api")
    brief = {
        "id": 1,
        "url": "http://localhost:8000/api/dcim/devices/1/",
        "name": "test",
    }

    def test_missing_marker_field_lazy_loads(self):
        device = Devices(copy.deepcopy(self.brief), self.api, None)
        full = dict(copy.deepcopy(self.brief), device_type={"id": 2})
        with patch(
            "pynetbox.core.query.Request.get", return_value=iter([full])
        ) as get:
            device_type = device.device_type
        self.assertEqual(get.call_count, 1)
        self.assertIsInstance(device_type, DeviceTypes)
        self.assertEqual(device_type.id, 2)

    def test_marker_field_omitted_by_server_raises_after_fetch(self):
        device = Devices(copy.deepcopy(self.brief), self.api, None)
        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(self.brief)]),
        ) as get:
            with self.assertRaises(AttributeError) as ctx:
                device.device_type
        self.assertEqual(get.call_count, 1)
        self.assertEqual(
            str(ctx.exception), 'object has no attribute "device_type"'
        )

    def test_hasattr_on_missing_marker_fetches_once(self):
        device = Devices(copy.deepcopy(self.brief), self.api, None)
        with patch(
            "pynetbox.core.query.Request.get",
            return_value=iter([copy.deepcopy(self.brief)]),
        ) as get:
            self.assertFalse(hasattr(device, "device_type"))
            self.assertFalse(hasattr(device, "device_type"))
        self.assertEqual(get.call_count, 1)

    def test_nested_brief_record_lazy_loads_marker_field(self):
        # FrontPorts declares `device = Devices`. Interfaces does not, so
        # its nested device is a plain Record and the test passes on main.
        port = FrontPorts(
            {
                "id": 5,
                "url": "http://localhost:8000/api/dcim/front-ports/5/",
                "name": "fp1",
                "device": copy.deepcopy(self.brief),
            },
            self.api,
            None,
        )
        full = dict(copy.deepcopy(self.brief), primary_ip={"id": 3})
        with patch(
            "pynetbox.core.query.Request.get", return_value=iter([full])
        ) as get:
            primary_ip = port.device.primary_ip
        self.assertEqual(get.call_count, 1)
        self.assertIsInstance(primary_ip, IpAddresses)

    def test_hydrated_falsy_value_returned(self):
        device = Devices(copy.deepcopy(self.brief), self.api, None)
        full = dict(copy.deepcopy(self.brief), serial="", asset_tag=None)
        with patch("pynetbox.core.query.Request.get", return_value=iter([full])):
            self.assertIsNone(device.asset_tag)
        self.assertEqual(device.serial, "")

    def test_property_reruns_after_hydration(self):
        class PropertyDevice(Devices):
            @property
            def serial_upper(self):
                # Raise before hydration so the lookup reaches
                # Record.__getattr__.
                if "serial" not in self.__dict__:
                    raise AttributeError("serial_upper")
                return self.serial.upper()

        device = PropertyDevice(copy.deepcopy(self.brief), self.api, None)
        full = dict(copy.deepcopy(self.brief), serial="abc")
        with patch("pynetbox.core.query.Request.get", return_value=iter([full])):
            self.assertEqual(device.serial_upper, "ABC")


class RecordSetTestCase(unittest.TestCase):
    ids = [1, 3, 5]

    @classmethod
    def init_recordset(cls):
        data = [
            {"id": i, "name": "dummy" + str(i), "status": "active"} for i in cls.ids
        ]
        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="test")

        class FakeRequest:
            def get(self):
                return iter(data)

            def patch(self):
                return iter(data)

        return RecordSet(Endpoint(api, app, "test"), FakeRequest())

    def test_delete(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            mock.return_value = True
            test_obj = RecordSetTestCase.init_recordset()
            test = test_obj.delete()
            mock.assert_called_with(
                verb="delete", data=[{"id": i} for i in RecordSetTestCase.ids]
            )
            self.assertTrue(test)

    def test_len_fetches_count_in_cursor_mode(self):
        """len() falls back to get_count() when count is None (cursor mode)."""
        from pynetbox.core.query import Request

        req = Request(
            http_session=Mock(),
            base="http://localhost:8000/api/dcim/devices",
            pagination="cursor",
        )
        # Simulate a cursor-paginated response: count omitted (null).
        req.http_session.get.return_value.ok = True
        req.http_session.get.return_value.json.side_effect = [
            {"count": None, "next": None, "previous": None, "results": [{"id": 1}]},
            {"count": 7, "next": None, "previous": None, "results": []},
        ]
        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="dcim")
        record_set = RecordSet(Endpoint(api, app, "devices"), req)
        self.assertEqual(len(record_set), 7)

    def test_update(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            mock.return_value = [
                {"id": i, "name": "dummy" + str(i), "status": "offline"}
                for i in RecordSetTestCase.ids
            ]
            test_obj = RecordSetTestCase.init_recordset()
            test = test_obj.update(status="offline")
            mock.assert_called_with(
                verb="patch",
                data=[{"id": i, "status": "offline"} for i in RecordSetTestCase.ids],
            )
            self.assertTrue(test)
