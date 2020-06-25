import unittest
from collections import OrderedDict

from pynetbox.core.query import url_param_builder


class TestQuery(unittest.TestCase):
    def test_url_param_builder(self):
        test_params = OrderedDict([("abc", "123"), ("xyz", "321"), ("enc", "#12"),])
        self.assertEqual(url_param_builder(test_params), "?abc=123&xyz=321&enc=%2312")
