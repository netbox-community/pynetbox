import unittest

import six

from pynetbox.core.query import Request

if six.PY3:
    from unittest.mock import patch, Mock, call
else:
    from mock import patch, Mock, call


class RequestTestCase(unittest.TestCase):
    def test_get_count(self):
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            filters={"q": "abcd"},
        )
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 42,
            "next": "http://localhost:8001/api/dcim/devices?limit=1&offset=1&q=abcd",
            "previous": False,
            "results": [],
        }
        expected = call(
            "http://localhost:8001/api/dcim/devices/?q=abcd&limit=1",
            headers={"accept": "application/json;"},
            verify=True,
        )
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        self.assertEqual(test_obj.http_session.get.call_args, expected)

    def test_get_count_no_filters(self):
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
        )
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 42,
            "next": "http://localhost:8001/api/dcim/devices?limit=1&offset=1",
            "previous": False,
            "results": [],
        }
        expected = call(
            "http://localhost:8001/api/dcim/devices/?limit=1",
            headers={"accept": "application/json;"},
            verify=True,
        )
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        self.assertEqual(test_obj.http_session.get.call_args, expected)
