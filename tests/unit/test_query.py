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
            "next": "http://localhost:8001/api/dcim/devices/?limit=1&offset=1&q=abcd",
            "previous": False,
            "results": [],
        }
        expected = call(
            "http://localhost:8001/api/dcim/devices/",
            params={"q": "abcd", "limit": 1},
            headers={"accept": "application/json;"},
        )
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            params={"q": "abcd", "limit": 1},
            headers={"accept": "application/json;"},
            json=None,
        )

    def test_get_count_no_filters(self):
        test_obj = Request(
            http_session=Mock(), base="http://localhost:8001/api/dcim/devices",
        )
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 42,
            "next": "http://localhost:8001/api/dcim/devices/?limit=1&offset=1",
            "previous": False,
            "results": [],
        }
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            params={"limit": 1},
            headers={"accept": "application/json;"},
            json=None,
        )

    def test_pagination(self):
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices/",
            limit=2,
            external_proxy=False
        )

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 6,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&offset=2",
            "previous": None,
            "results": [
                {'id': 87861, 'url': 'https://localhost:8001/api/dcim/devices/87861/', 'name': 'test87861'},
                {'id': 87862, 'url': 'https://localhost:8001/api/dcim/devices/87862/', 'name': 'test87862'},
                ],
        }
        test = test_obj.get()
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            headers={"accept": "application/json;"},
            params={"limit": 2},
            json=None,
        )
        self.assertEqual(req, {'id': 87861, 'url': 'https://localhost:8001/api/dcim/devices/87861/', 'name': 'test87861'})
        req = next(test)
        self.assertEqual(req, {'id': 87862, 'url': 'https://localhost:8001/api/dcim/devices/87862/', 'name': 'test87862'})

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 2,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&offset=4",
            "previous": "http://localhost:8001/api/dcim/devices/?limit=2",
            "results": [
                {'id': 87863, 'url': 'https://localhost:8001/api/dcim/devices/87863/', 'name': 'test87863'},
                {'id': 87864, 'url': 'https://localhost:8001/api/dcim/devices/87864/', 'name': 'test87864'},
                ],
        }
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            headers={"accept": "application/json;"},
            params={"limit": 2, "offset": 2},
            json=None,
        )
        self.assertEqual(req, {'id': 87863, 'url': 'https://localhost:8001/api/dcim/devices/87863/', 'name': 'test87863'})
        req = next(test)
        self.assertEqual(req, {'id': 87864, 'url': 'https://localhost:8001/api/dcim/devices/87864/', 'name': 'test87864'})

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 2,
            "next": None,
            "previous": "http://localhost:8001/api/dcim/devices/?limit=2&offset=4",
            "results": [
                {'id': 87865, 'url': 'https://localhost:8001/api/dcim/devices/87865/', 'name': 'test87865'},
                {'id': 87866, 'url': 'https://localhost:8001/api/dcim/devices/87866/', 'name': 'test87866'},
                ],
        }
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/?limit=2&offset=4",
            headers={"accept": "application/json;"},
            params={},
            json=None,
        )
        self.assertEqual(req, {'id': 87865, 'url': 'https://localhost:8001/api/dcim/devices/87865/', 'name': 'test87865'})
        req = next(test)
        self.assertEqual(req, {'id': 87866, 'url': 'https://localhost:8001/api/dcim/devices/87866/', 'name': 'test87866'})

    def test_pagination_behind_external_proxy(self):
        test_obj = Request(
            http_session=Mock(),
            base="http://example.com/netbox/api/dcim/devices",
            limit=2,
            external_proxy=True,
        )

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 6,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&offset=2",
            "previous": None,
            "results": [
                {'id': 87861, 'url': 'https://localhost:8001/api/dcim/devices/87861/', 'name': 'test87861'},
                {'id': 87862, 'url': 'https://localhost:8001/api/dcim/devices/87862/', 'name': 'test87862'},
                ],
        }
        test = test_obj.get()
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://example.com/netbox/api/dcim/devices/",
            headers={"accept": "application/json;"},
            params={"limit": 2},
            json=None,
        )
        self.assertEqual(req, {'id': 87861, 'url': 'https://localhost:8001/api/dcim/devices/87861/', 'name': 'test87861'})
        req = next(test)
        self.assertEqual(req, {'id': 87862, 'url': 'https://localhost:8001/api/dcim/devices/87862/', 'name': 'test87862'})

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 2,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&offset=4",
            "previous": "http://localhost:8001/api/dcim/devices/?limit=2",
            "results": [
                {'id': 87863, 'url': 'https://localhost:8001/api/dcim/devices/87863/', 'name': 'test87863'},
                {'id': 87864, 'url': 'https://localhost:8001/api/dcim/devices/87864/', 'name': 'test87864'},
                ],
        }
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://example.com/netbox/api/dcim/devices/",
            params={"limit": 2, "offset": 2},
            headers={"accept": "application/json;"},
            json=None,
        )
        self.assertEqual(req, {'id': 87863, 'url': 'https://localhost:8001/api/dcim/devices/87863/', 'name': 'test87863'})
        req = next(test)
        self.assertEqual(req, {'id': 87864, 'url': 'https://localhost:8001/api/dcim/devices/87864/', 'name': 'test87864'})

        test_obj.http_session.get.return_value.json.return_value = {
            "count": 2,
            "next": None,
            "previous": "http://localhost:8001/api/dcim/devices/?limit=2&offset=4",
            "results": [
                {'id': 87865, 'url': 'https://localhost:8001/api/dcim/devices/87865/', 'name': 'test87865'},
                {'id': 87866, 'url': 'https://localhost:8001/api/dcim/devices/87866/', 'name': 'test87866'},
                ],
        }
        req = next(test)
        test_obj.http_session.get.assert_called_with(
            "http://example.com/netbox/api/dcim/devices/?limit=2&offset=4",
            headers={"accept": "application/json;"},
            params={},
            json=None,
        )
        self.assertEqual(req, {'id': 87865, 'url': 'https://localhost:8001/api/dcim/devices/87865/', 'name': 'test87865'})
        req = next(test)
        self.assertEqual(req, {'id': 87866, 'url': 'https://localhost:8001/api/dcim/devices/87866/', 'name': 'test87866'})
