import concurrent.futures
import unittest
from unittest.mock import Mock, patch

import pynetbox

from .util import Response

host = "http://localhost:8000"

def_kwargs = {
    "token": "abc123",
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
        "requests.sessions.Session.post",
        return_value=Response(),
    )
    def test_get(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        self.assertTrue(api)

    @patch(
        "requests.sessions.Session.post",
        return_value=Response(),
    )
    def test_sanitize_url(self, *_):
        api = pynetbox.api("http://localhost:8000/", **def_kwargs)
        self.assertTrue(api)
        self.assertEqual(api.base_url, "http://localhost:8000/api")


class ApiThreadPoolTestCase(unittest.TestCase):
    @patch("requests.sessions.Session.post", return_value=Response())
    def test_threadpool_defaults(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        self.assertIsNone(api.thread_pool_executor)
        self.assertEqual(api.max_workers, 4)

    @patch("requests.sessions.Session.post", return_value=Response())
    def test_threadpool_custom_values_stored(self, *_):
        executor = concurrent.futures.ThreadPoolExecutor
        api = pynetbox.api(
            host,
            thread_pool_executor=executor,
            max_workers=12,
            **def_kwargs,
        )
        self.assertIs(api.thread_pool_executor, executor)
        self.assertEqual(api.max_workers, 12)

    @patch("requests.sessions.Session.post", return_value=Response())
    def test_threadpool_invalid_max_workers(self, *_):
        for invalid in (0, -1):
            with self.assertRaises(ValueError):
                pynetbox.api(host, max_workers=invalid, **def_kwargs)

    @patch("requests.sessions.Session.post", return_value=Response())
    @patch("pynetbox.core.endpoint.Request")
    def test_threadpool_propagated_to_request(self, request_mock, *_):
        executor = concurrent.futures.ThreadPoolExecutor
        api = pynetbox.api(
            host,
            threading=True,
            thread_pool_executor=executor,
            max_workers=9,
            **def_kwargs,
        )
        # Avoid iterating the mocked RecordSet; we only care about the kwargs
        # passed into the Request that backs .all().
        request_mock.return_value = Mock()
        api.dcim.devices.all()

        _, kwargs = request_mock.call_args
        self.assertIs(kwargs["thread_pool_executor"], executor)
        self.assertEqual(kwargs["max_workers"], 9)
        self.assertTrue(kwargs["threading"])


class ApiVersionTestCase(unittest.TestCase):
    class ResponseHeadersWithVersion:
        headers = {"API-Version": "1.999"}
        ok = True

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseHeadersWithVersion(),
    )
    def test_api_version(self, *_):
        api = pynetbox.api(
            host,
        )
        self.assertEqual(api.version, "1.999")

    class ResponseHeadersWithoutVersion:
        headers = {}
        ok = True

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseHeadersWithoutVersion(),
    )
    def test_api_version_not_found(self, *_):
        api = pynetbox.api(
            host,
        )
        self.assertEqual(api.version, "")


class ApiStatusTestCase(unittest.TestCase):
    class ResponseWithStatus:
        ok = True

        def json(self):
            return {
                "netbox-version": "0.9.9",
            }

    @patch(
        "requests.sessions.Session.get",
        return_value=ResponseWithStatus(),
    )
    def test_api_status(self, *_):
        api = pynetbox.api(
            host,
        )
        self.assertEqual(api.status()["netbox-version"], "0.9.9")


class ApiCreateTokenTestCase(unittest.TestCase):
    @patch(
        "requests.sessions.Session.post",
        return_value=Response(fixture="api/token_provision_v1_legacy.json"),
    )
    def test_create_token_v1_legacy(self, *_):
        """Old NetBox (pre-4.5): response has only 'key' field."""
        api = pynetbox.api(host)
        token = api.create_token("user", "pass")
        self.assertTrue(isinstance(token, pynetbox.core.response.Record))
        self.assertEqual(token.key, "1234567890123456789012345678901234567890")
        self.assertEqual(api.token, "1234567890123456789012345678901234567890")

    @patch(
        "requests.sessions.Session.post",
        return_value=Response(fixture="api/token_provision_v1_with_token.json"),
    )
    def test_create_token_v1_with_token(self, *_):
        """NetBox 4.5+ v1 tokens: response includes 'token' field; use it directly."""
        api = pynetbox.api(host)
        token = api.create_token("user", "pass")
        self.assertTrue(isinstance(token, pynetbox.core.response.Record))
        self.assertEqual(token.key, "1234567890123456789012345678901234567890")
        self.assertEqual(api.token, "plaintexttoken7890abcdef1234567890abcdef")

    @patch(
        "requests.sessions.Session.post",
        return_value=Response(fixture="api/token_provision_v2.json"),
    )
    def test_create_token_v2(self, *_):
        """NetBox 4.5+ v2 tokens: auth token must be 'nbt_<key>.<token>'."""
        api = pynetbox.api(host)
        token = api.create_token("user", "pass")
        self.assertTrue(isinstance(token, pynetbox.core.response.Record))
        self.assertEqual(token.key, "shortkey1234567")
        self.assertEqual(
            api.token, "nbt_shortkey1234567.plaintexttoken7890abcdef1234567890abcdef"
        )
