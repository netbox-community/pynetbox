import unittest

import six

from pynetbox.models.extras import ConfigContexts


class ExtrasTestCase(unittest.TestCase):
    def test_config_contexts(self):
        test_values = {
            "data": {"test_int": 123, "test_str": "testing", "test_list": [1, 2, 3],}
        }
        test = ConfigContexts(test_values, None, None)
        self.assertTrue(test)

    def test_config_contexts_diff_str(self):
        test_values = {
            "data": {
                "test_int": 123,
                "test_str": "testing",
                "test_list": [1, 2, 3],
                "test_dict": {"foo": "bar"},
            }
        }
        test = ConfigContexts(test_values, None, None)
        test.data["test_str"] = "bar"
        self.assertEqual(test._diff(), {"data"})

    def test_config_contexts_diff_dict(self):
        test_values = {
            "data": {
                "test_int": 123,
                "test_str": "testing",
                "test_list": [1, 2, 3],
                "test_dict": {"foo": "bar"},
            }
        }
        test = ConfigContexts(test_values, None, None)
        test.data["test_dict"].update({"bar": "foo"})
        self.assertEqual(test._diff(), {"data"})
