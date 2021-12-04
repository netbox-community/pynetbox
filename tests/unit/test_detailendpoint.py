import unittest

import six

import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


nb = pynetbox.api("http://localhost:8000")


class DetailEndpointTestCase(unittest.TestCase):
    def test_detail_endpoint_create_single(self):
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "prefix": "1.2.3.0/24"},
        ):
            prefix_obj = nb.ipam.prefixes.get(123)
            self.assertEqual(prefix_obj.prefix, "1.2.3.0/24")
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"address": "1.2.3.1/24"},
        ):
            ip_obj = prefix_obj.available_ips.create()
            self.assertEqual(ip_obj.address, "1.2.3.1/24")

    def test_detail_endpoint_create_list(self):
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "prefix": "1.2.3.0/24"},
        ):
            prefix_obj = nb.ipam.prefixes.get(123)
            self.assertEqual(prefix_obj.prefix, "1.2.3.0/24")
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=[{"address": "1.2.3.1/24"}, {"address": "1.2.3.2/24"}],
        ):
            ip_list = prefix_obj.available_ips.create([{} for _ in range(2)])
            self.assertTrue(isinstance(ip_list, list))
            self.assertEqual(len(ip_list), 2)
