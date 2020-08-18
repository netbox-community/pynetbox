import unittest

import six

from pynetbox.core.response import Record

if six.PY3:
    from unittest.mock import Mock
else:
    from mock import Mock


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

    def test_serialize_tag_set(self):
        test_values = {"id": 123, "tags": ["foo", "bar", "foo"]}
        test = Record(test_values, None, None).serialize()
        self.assertEqual(len(test["tags"]), 2)

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

    def test_choices_idempotence_prev27(self):
        test_values = {
            "id": 123,
            "choices_test": {"value": 1, "label": "test",},
        }
        test = Record(test_values, None, None)
        test.choices_test = 1
        self.assertFalse(test._diff())

    def test_choices_idempotence_v27(self):
        test_values = {
            "id": 123,
            "choices_test": {"value": "test", "label": "test", "id": 1,},
        }
        test = Record(test_values, None, None)
        test.choices_test = "test"
        self.assertFalse(test._diff())

    def test_choices_idempotence_v28(self):
        test_values = {
            "id": 123,
            "choices_test": {"value": "test", "label": "test",},
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
                    "url": "http://localhost:8080/api/test-app/test-endpoint/",
                },
            },
            app,
            endpoint,
        )
        test.child.name = "test321"
        test.child.save()
        self.assertEqual(
            app.http_session.patch.call_args[0][0],
            "http://localhost:8080/api/test-app/test-endpoint/",
        )

    def test_endpoint_from_url(self):
        test = Record(
            {
                "id": 123,
                "name": "test",
                "url": "http://localhost:8080/api/test-app/test-endpoint/1/",
            },
            Mock(),
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
