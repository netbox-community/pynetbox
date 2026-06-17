import concurrent.futures
import unittest
from unittest.mock import Mock

from pynetbox.core.query import Request, _is_v2_token


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
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            params={"q": "abcd", "limit": 1, "brief": 1},
            headers={"accept": "application/json"},
            json=None,
        )

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
        test_obj.http_session.get.ok = True
        test = test_obj.get_count()
        self.assertEqual(test, 42)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            params={"limit": 1, "brief": 1},
            headers={"accept": "application/json"},
            json=None,
        )

    def test_get_manual_pagination(self):
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            limit=10,
            offset=20,
        )
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 4,
            "next": "http://localhost:8001/api/dcim/devices?limit=10&offset=30",
            "previous": False,
            "results": [1, 2, 3, 4],
        }
        test_obj.http_session.get.ok = True
        generator = test_obj.get()
        self.assertEqual(len(list(generator)), 4)
        test_obj.http_session.get.assert_called_with(
            "http://localhost:8001/api/dcim/devices/",
            params={"offset": 20, "limit": 10},
            headers={"accept": "application/json"},
            json=None,
        )


class CursorPaginationTestCase(unittest.TestCase):
    """Tests for cursor-based pagination (NetBox 4.6+)."""

    def test_first_request_sends_start_not_offset(self):
        """Cursor mode should send start=0 (and never offset) on the first call."""
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            limit=2,
            pagination="cursor",
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": None,
            "next": None,
            "previous": None,
            "results": [{"id": 1}, {"id": 2}],
        }

        list(test_obj.get())

        call_args = test_obj.http_session.get.call_args
        self.assertEqual(call_args.kwargs["params"], {"limit": 2, "start": 0})
        self.assertNotIn("offset", call_args.kwargs["params"])

    def test_follows_next_links_sequentially(self):
        """Cursor mode should follow server next links until exhausted."""
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            limit=2,
            pagination="cursor",
        )
        page1 = {
            "count": None,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&start=3",
            "previous": None,
            "results": [{"id": 1}, {"id": 2}],
        }
        page2 = {
            "count": None,
            "next": "http://localhost:8001/api/dcim/devices/?limit=2&start=5",
            "previous": None,
            "results": [{"id": 3}, {"id": 4}],
        }
        page3 = {
            "count": None,
            "next": None,
            "previous": None,
            "results": [{"id": 5}],
        }
        responses = [page1, page2, page3]
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.side_effect = responses

        results = list(test_obj.get())

        self.assertEqual([r["id"] for r in results], [1, 2, 3, 4, 5])
        # Subsequent pages are fetched via the server-provided next URLs.
        next_urls = [
            c.args[0] for c in test_obj.http_session.get.call_args_list[1:]
        ]
        self.assertEqual(
            next_urls,
            [
                "http://localhost:8001/api/dcim/devices/?limit=2&start=3",
                "http://localhost:8001/api/dcim/devices/?limit=2&start=5",
            ],
        )

    def test_explicit_offset_falls_back_to_offset(self):
        """An explicit offset opts out of cursor mode (mutually exclusive)."""
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            limit=10,
            offset=20,
            pagination="cursor",
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [1, 2, 3, 4],
        }

        list(test_obj.get())

        call_args = test_obj.http_session.get.call_args
        self.assertEqual(call_args.kwargs["params"], {"offset": 20, "limit": 10})
        self.assertNotIn("start", call_args.kwargs["params"])

    def test_ordering_filter_warns(self):
        """An 'ordering' filter has no effect in cursor mode, so warn."""
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            filters={"ordering": "name"},
            limit=2,
            pagination="cursor",
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": None,
            "next": None,
            "previous": None,
            "results": [{"id": 1}],
        }

        with self.assertWarns(UserWarning) as ctx:
            list(test_obj.get())
        self.assertIn("ordering", str(ctx.warning))

    def test_ordering_filter_no_warn_offset(self):
        """Offset pagination honors 'ordering', so it must not warn."""
        import warnings

        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            filters={"ordering": "name"},
            limit=2,
            pagination="offset",
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": 1}],
        }

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            list(test_obj.get())

    def test_get_count_fetched_when_null(self):
        """get_count() refetches when cursor pagination left count as None."""
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            pagination="cursor",
        )
        test_obj.count = None
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 99,
            "next": None,
            "previous": None,
            "results": [],
        }

        self.assertEqual(test_obj.get_count(), 99)
        call_args = test_obj.http_session.get.call_args
        self.assertEqual(call_args.kwargs["params"], {"limit": 1, "brief": 1})


class ConcurrentGetTestCase(unittest.TestCase):
    """Tests for the threaded pagination executor wiring."""

    def _request(self, **kwargs):
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            **kwargs,
        )
        # Stub the per-page HTTP call so concurrent_get has something to fan out.
        test_obj._make_call = Mock(return_value={"results": [1, 2]})
        return test_obj

    def test_defaults_to_threadpoolexecutor(self):
        """Without an override, the stdlib ThreadPoolExecutor is used."""
        test_obj = self._request()
        self.assertIs(
            test_obj.thread_pool_executor, concurrent.futures.ThreadPoolExecutor
        )
        self.assertEqual(test_obj.max_workers, 4)

    def test_custom_executor_is_used(self):
        """A custom executor factory is invoked with the configured max_workers."""
        calls = {}

        class RecordingExecutor(concurrent.futures.ThreadPoolExecutor):
            def __init__(self, max_workers=None):
                calls["max_workers"] = max_workers
                calls["used"] = True
                super().__init__(max_workers=max_workers)

        test_obj = self._request(
            thread_pool_executor=RecordingExecutor,
            max_workers=7,
        )

        ret = []
        test_obj.concurrent_get(ret, page_size=2, page_offsets=[2, 4, 6])

        self.assertTrue(calls.get("used"))
        self.assertEqual(calls["max_workers"], 7)
        # Three offsets, two results per page.
        self.assertEqual(len(ret), 6)
        self.assertEqual(test_obj._make_call.call_count, 3)

    def test_none_executor_falls_back_to_default(self):
        """Passing None explicitly resolves to the stdlib default."""
        test_obj = self._request(thread_pool_executor=None)
        self.assertIs(
            test_obj.thread_pool_executor, concurrent.futures.ThreadPoolExecutor
        )


class TokenDetectionTestCase(unittest.TestCase):
    """Tests for v1 vs v2 token detection."""

    def test_v1_token_without_dot(self):
        """V1 tokens are simple strings without dots."""
        token = "d6f4e314a5b5fefd164995169f28ae32d987704f"
        self.assertFalse(_is_v2_token(token))

    def test_v2_token_with_prefix(self):
        """V2 tokens have nbt_ prefix for secrets detection."""
        token = "nbt_abc123.def456ghi789"
        self.assertTrue(_is_v2_token(token))


class TokenAuthorizationHeaderTestCase(unittest.TestCase):
    """Tests for authorization header format with v1 and v2 tokens."""

    def test_v1_token_uses_token_header(self):
        """V1 tokens should use 'Token' authorization header."""
        v1_token = "d6f4e314a5b5fefd164995169f28ae32d987704f"
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            token=v1_token,
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": 1, "name": "test"}],
        }

        list(test_obj.get())

        # Check that the authorization header uses "Token" format
        call_args = test_obj.http_session.get.call_args
        self.assertIn("authorization", call_args.kwargs["headers"])
        self.assertEqual(
            call_args.kwargs["headers"]["authorization"], f"Token {v1_token}"
        )

    def test_v2_token_with_prefix_uses_bearer_header(self):
        """V2 tokens with prefix should use 'Bearer' authorization header."""
        v2_token = "nbt_abc123.def456ghi789"
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api/dcim/devices",
            token=v2_token,
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": 1, "name": "test"}],
        }

        list(test_obj.get())

        # Check that the authorization header uses "Bearer" format
        call_args = test_obj.http_session.get.call_args
        self.assertIn("authorization", call_args.kwargs["headers"])
        self.assertEqual(
            call_args.kwargs["headers"]["authorization"], f"Bearer {v2_token}"
        )

    def test_get_status_with_v1_token(self):
        """get_status should use 'Token' header for v1 tokens."""
        v1_token = "d6f4e314a5b5fefd164995169f28ae32d987704f"
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api",
            token=v1_token,
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "django-version": "4.0",
            "netbox-version": "4.4.0",
        }

        test_obj.get_status()

        # Check that the authorization header uses "Token" format
        call_args = test_obj.http_session.get.call_args
        self.assertIn("authorization", call_args.kwargs["headers"])
        self.assertEqual(
            call_args.kwargs["headers"]["authorization"], f"Token {v1_token}"
        )

    def test_get_status_with_v2_token(self):
        """get_status should use 'Bearer' header for v2 tokens."""
        v2_token = "nbt_abc123.def456ghi789"
        test_obj = Request(
            http_session=Mock(),
            base="http://localhost:8001/api",
            token=v2_token,
        )
        test_obj.http_session.get.return_value.ok = True
        test_obj.http_session.get.return_value.json.return_value = {
            "django-version": "4.0",
            "netbox-version": "4.5.0",
        }

        test_obj.get_status()

        # Check that the authorization header uses "Bearer" format
        call_args = test_obj.http_session.get.call_args
        self.assertIn("authorization", call_args.kwargs["headers"])
        self.assertEqual(
            call_args.kwargs["headers"]["authorization"], f"Bearer {v2_token}"
        )
