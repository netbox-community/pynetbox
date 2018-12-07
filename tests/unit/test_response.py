import unittest

from pynetbox.core.response import Record


class RecordTestCase(unittest.TestCase):

    def test_serialize_list_of_records(self):
        test_values = {
            'id': 123,
            "tagged_vlans": [
                {
                    "id": 1,
                    "url": "http://localhost:8000/api/ipam/vlans/1/",
                    "vid": 1,
                    "name": "test1",
                    "display_name": "test1"
                },
                {
                    "id": 2,
                    "url": "http://localhost:8000/api/ipam/vlans/2/",
                    "vid": 2,
                    "name": "test 2",
                    "display_name": "test2"
                }
            ],
        }
        test_obj = Record(test_values, None, None)
        test = test_obj.serialize()
        self.assertEqual(test['tagged_vlans'], [1, 2])

    def test_serialize_list_of_ints(self):
        test_values = {
            'id': 123,
            'units': [12],
        }
        test_obj = Record(test_values, None, None)
        test = test_obj.serialize()
        self.assertEqual(test['units'], [12])

    def test_serialize_tag_set(self):
        test_values = {
            'id': 123,
            'tags': [
                'foo',
                'bar',
                'foo',
            ],
        }
        test = Record(test_values, None, None).serialize()
        self.assertEqual(len(test['tags']), 2)

    def test_diff(self):
        test_values = {
            'id': 123,
            'custom_fields': {
                'foo': 'bar'
            },
            'string_field': 'foobar',
            'int_field': 1,
            "nested_dict": {
                "id": 222,
                "name": 'bar',
            },
            'tags': [
                'foo',
                'bar',
            ],
            'int_list': [
                123,
                321,
                231,
            ],
        }
        test = Record(test_values, None, None)
        test.tags.append('baz')
        test.nested_dict = 1
        test.string_field = 'foobaz'
        self.assertEqual(test._diff(), {'tags', 'nested_dict', 'string_field'})
