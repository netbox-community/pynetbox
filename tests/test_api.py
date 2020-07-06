import unittest
import six

import pynetbox
from .util import Response

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

host = "http://localhost:8000"

def_kwargs = {
    "token": "abc123",
    "private_key_file": "tests/fixtures/api/get_session_key.json",
}

# Keys are app names, values are arbitrarily selected endpoints
# We use dcim and ipam since they have unique app classes
# and circuits because it does not. We don't add other apps/endpoints
# beyond 'circuits' as they all use the same code as each other
endpoints = {
    "dcim": "devices",
    "ipam": "prefixes",
    "circuits": "circuits",
}


class ApiTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.requests.sessions.Session.post",
        return_value=Response(fixture="api/get_session_key.json"),
    )
    def test_get(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        self.assertTrue(api)

    @patch(
        "pynetbox.core.query.requests.sessions.Session.post",
        return_value=Response(fixture="api/get_session_key.json"),
    )
    def test_sanitize_url(self, *_):
        api = pynetbox.api("http://localhost:8000/", **def_kwargs)
        self.assertTrue(api)
        self.assertEqual(api.base_url, "http://localhost:8000/api")


class ApiVersionTestCase(unittest.TestCase):
    class ResponseHeadersWithVersion:
        headers = {"API-Version": "1.999"}
        ok = True

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=ResponseHeadersWithVersion(),
    )
    def test_api_version(self, *_):
        api = pynetbox.api(host,)
        self.assertEqual(api.version, "1.999")

    class ResponseHeadersWithoutVersion:
        headers = {}
        ok = True

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=ResponseHeadersWithoutVersion(),
    )
    def test_api_version_not_found(self, *_):
        api = pynetbox.api(host,)
        self.assertEqual(api.version, "")
