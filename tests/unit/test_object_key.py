"""Tests for encoding object ids in request URLs (issue #825)."""

import unittest
from unittest.mock import Mock

from pynetbox.core.endpoint import DetailEndpoint, Endpoint
from pynetbox.core.query import Request
from pynetbox.core.response import PathableRecord, Record
from pynetbox.extensions.branching import Branches
from pynetbox.models.dcim import TraceableRecord

BASE = "http://localhost:8000/api/dcim/devices/"
UNSAFE_KEYS = {
    "../sites/1": "..%2Fsites%2F1",
    "1/trace": "1%2Ftrace",
    "1?brief=1": "1%3Fbrief%3D1",
    "1#x": "1%23x",
}


def make_api():
    api = Mock()
    api.token = "abc123"
    api.base_url = "http://localhost:8000/api"
    resp = api.http_session.get.return_value
    resp.ok = True
    resp.json.return_value = []
    api.http_session.patch.return_value.ok = True
    api.http_session.patch.return_value.json.return_value = {"id": 1}
    api.http_session.delete.return_value.ok = True
    return api


def make_record(api, cls=Record):
    endpoint = Mock()
    endpoint.url = BASE
    endpoint.name = "devices"
    return cls({"id": 1, "name": "test"}, api, endpoint)


def called_url(method):
    return method.call_args[0][0]


class RequestUrlTestCase(unittest.TestCase):
    def test_int_key(self):
        self.assertEqual(Request(BASE, Mock(), key=1).url, BASE + "1/")

    def test_no_key_uses_list_url(self):
        self.assertEqual(Request(BASE, Mock()).url, BASE)

    def test_zero_key_is_not_list_url(self):
        self.assertEqual(Request(BASE, Mock(), key=0).url, BASE + "0/")

    def test_unsafe_keys_are_encoded(self):
        for key, encoded in UNSAFE_KEYS.items():
            with self.subTest(key=key):
                self.assertEqual(
                    Request(BASE, Mock(), key=key).url, BASE + encoded + "/"
                )

    def test_empty_key_raises(self):
        with self.assertRaises(ValueError):
            Request(BASE, Mock(), key="")

    def test_suffix(self):
        self.assertEqual(
            Request(BASE, Mock(), key=1, suffix="trace").url, BASE + "1/trace/"
        )
        self.assertEqual(
            Request(BASE, Mock(), key="../1", suffix="trace").url,
            BASE + "..%2F1/trace/",
        )

    def test_suffix_without_key_raises(self):
        with self.assertRaises(ValueError):
            Request(BASE, Mock(), suffix="trace")


class EndpointGetTestCase(unittest.TestCase):
    def make_endpoint(self, api):
        app = Mock()
        app.name = "dcim"
        return Endpoint(api, app, "devices")

    def test_get_encodes_key(self):
        api = make_api()
        api.http_session.get.return_value.json.return_value = {"id": 1}
        self.make_endpoint(api).get("../sites/1")
        self.assertEqual(
            called_url(api.http_session.get),
            "http://localhost:8000/api/dcim/devices/..%2Fsites%2F1/",
        )

    def test_get_zero_requests_detail_url(self):
        api = make_api()
        api.http_session.get.return_value.json.return_value = {"id": 0}
        self.make_endpoint(api).get(0)
        self.assertEqual(
            called_url(api.http_session.get),
            "http://localhost:8000/api/dcim/devices/0/",
        )

    def test_get_empty_key_raises(self):
        api = make_api()
        with self.assertRaises(ValueError):
            self.make_endpoint(api).get("")
        api.http_session.get.assert_not_called()


class RecordKeyTestCase(unittest.TestCase):
    def test_save_encodes_id(self):
        api = make_api()
        record = make_record(api)
        record.id = "../../users/users/1"
        record.name = "changed"
        record.save()
        self.assertEqual(
            called_url(api.http_session.patch),
            BASE + "..%2F..%2Fusers%2Fusers%2F1/",
        )

    def test_delete_encodes_id(self):
        api = make_api()
        record = make_record(api)
        record.id = "../../users/users/1"
        record.delete()
        self.assertEqual(
            called_url(api.http_session.delete),
            BASE + "..%2F..%2Fusers%2Fusers%2F1/",
        )

    def test_delete_without_id_raises(self):
        for value in (None, ""):
            with self.subTest(id=value):
                api = make_api()
                record = make_record(api)
                record.id = value
                with self.assertRaises(ValueError):
                    record.delete()
                api.http_session.delete.assert_not_called()

    def test_trace_url(self):
        api = make_api()
        make_record(api, TraceableRecord).trace()
        self.assertEqual(called_url(api.http_session.get), BASE + "1/trace/")

    def test_trace_encodes_id(self):
        api = make_api()
        record = make_record(api, TraceableRecord)
        record.id = "../sites/1"
        record.trace()
        self.assertEqual(
            called_url(api.http_session.get), BASE + "..%2Fsites%2F1/trace/"
        )

    def test_paths_url(self):
        api = make_api()
        make_record(api, PathableRecord).paths()
        self.assertEqual(called_url(api.http_session.get), BASE + "1/paths/")

    def test_paths_encodes_id(self):
        api = make_api()
        record = make_record(api, PathableRecord)
        record.id = "../sites/1"
        record.paths()
        self.assertEqual(
            called_url(api.http_session.get), BASE + "..%2Fsites%2F1/paths/"
        )


class DetailUrlTestCase(unittest.TestCase):
    def test_detail_endpoint_url(self):
        api = make_api()
        detail = DetailEndpoint(make_record(api), "available-ips")
        self.assertEqual(detail.url, BASE + "1/available-ips/")
        list(detail.list())
        self.assertEqual(called_url(api.http_session.get), BASE + "1/available-ips/")

    def test_detail_endpoint_encodes_id(self):
        api = make_api()
        record = make_record(api)
        record.id = "../sites/1"
        DetailEndpoint(record, "available-ips").create({})
        self.assertEqual(
            called_url(api.http_session.post), BASE + "..%2Fsites%2F1/available-ips/"
        )

    def test_branch_action_encodes_id(self):
        api = make_api()
        api.http_session.post.return_value.ok = True
        api.http_session.post.return_value.status_code = 200
        api.http_session.post.return_value.json.return_value = {}
        branch = make_record(api, Branches)
        branch.id = "../../dcim/devices/1"
        branch.sync()
        self.assertEqual(
            called_url(api.http_session.post),
            BASE + "..%2F..%2Fdcim%2Fdevices%2F1/sync/",
        )
