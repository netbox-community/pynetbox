"""Tests for passing changelog_message on writes (issue #793)."""

import unittest
from unittest.mock import Mock, patch

from pynetbox.core.endpoint import Endpoint
from pynetbox.core.response import Record, RecordSet

IDS = [1, 3, 5]


def make_record():
    api = Mock()
    api.token = "abc123"
    api.base_url = "http://localhost:8000/api"
    endpoint = Mock()
    endpoint.url = "http://localhost:8000/api/dcim/devices/"
    endpoint.name = "devices"
    record = Record(
        {
            "id": 1,
            "name": "test",
            "serial": "",
            "url": "http://localhost:8000/api/dcim/devices/1/",
        },
        api,
        endpoint,
    )
    api.http_session.patch.return_value.ok = True
    api.http_session.patch.return_value.json.return_value = {
        "id": 1,
        "name": "test",
        "serial": "ABC123",
        "url": "http://localhost:8000/api/dcim/devices/1/",
    }
    api.http_session.delete.return_value.ok = True
    return record, api


def make_endpoint():
    api = Mock(base_url="http://localhost:8000/api")
    app = Mock(name="test")
    return Endpoint(api, app, "test")


def make_recordset():
    data = [{"id": i, "name": "dummy" + str(i), "status": "active"} for i in IDS]

    class FakeRequest:
        def get(self):
            return iter(data)

    return RecordSet(make_endpoint(), FakeRequest())


class RecordChangelogMessageTestCase(unittest.TestCase):
    def test_save_sends_changelog_message(self):
        record, api = make_record()
        record.serial = "ABC123"
        self.assertTrue(record.save(changelog_message="audit"))
        self.assertEqual(
            api.http_session.patch.call_args.kwargs["json"],
            {"serial": "ABC123", "changelog_message": "audit"},
        )

    def test_save_without_changes_sends_nothing(self):
        record, api = make_record()
        self.assertFalse(record.save(changelog_message="audit"))
        api.http_session.patch.assert_not_called()

    def test_save_without_changelog_message(self):
        record, api = make_record()
        record.serial = "ABC123"
        record.save()
        self.assertEqual(
            api.http_session.patch.call_args.kwargs["json"], {"serial": "ABC123"}
        )

    def test_update_sends_changelog_message(self):
        record, api = make_record()
        self.assertTrue(record.update({"serial": "ABC123"}, changelog_message="audit"))
        self.assertEqual(
            api.http_session.patch.call_args.kwargs["json"],
            {"serial": "ABC123", "changelog_message": "audit"},
        )

    def test_changelog_message_attribute_is_not_resent(self):
        """A message set as an attribute is sent once, not on every later save()."""
        record, api = make_record()
        record.update({"serial": "ABC123", "changelog_message": "audit"})
        self.assertEqual(
            api.http_session.patch.call_args.kwargs["json"],
            {"serial": "ABC123", "changelog_message": "audit"},
        )
        self.assertEqual(record.updates(), {})
        self.assertFalse(record.save())
        self.assertEqual(api.http_session.patch.call_count, 1)

    def test_delete_sends_changelog_message(self):
        record, api = make_record()
        self.assertTrue(record.delete(changelog_message="decommissioned"))
        self.assertEqual(
            api.http_session.delete.call_args.kwargs["json"],
            {"changelog_message": "decommissioned"},
        )
        self.assertEqual(
            api.http_session.delete.call_args.kwargs["headers"]["Content-Type"],
            "application/json",
        )

    def test_delete_without_changelog_message_sends_no_body(self):
        record, api = make_record()
        self.assertTrue(record.delete())
        self.assertIsNone(api.http_session.delete.call_args.kwargs["json"])


class EndpointChangelogMessageTestCase(unittest.TestCase):
    def test_create_passes_changelog_message_through(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value={"id": 1}
        ) as mock:
            make_endpoint().create(name="test", changelog_message="new")
            mock.assert_called_with(
                verb="post", data={"name": "test", "changelog_message": "new"}
            )

    def test_update_applies_changelog_message(self):
        with patch("pynetbox.core.query.Request._make_call", return_value=[]) as mock:
            objects = [{"id": i, "status": "offline"} for i in IDS]
            make_endpoint().update(objects, changelog_message="bulk")
            mock.assert_called_with(
                verb="patch",
                data=[
                    {"changelog_message": "bulk", "id": i, "status": "offline"}
                    for i in IDS
                ],
            )
            # The caller's dicts are not mutated
            self.assertNotIn("changelog_message", objects[0])

    def test_update_keeps_per_object_changelog_message(self):
        with patch("pynetbox.core.query.Request._make_call", return_value=[]) as mock:
            objects = [
                {"id": 1, "status": "offline", "changelog_message": "own"},
                {"id": 3, "status": "offline"},
            ]
            make_endpoint().update(objects, changelog_message="bulk")
            data = mock.call_args.kwargs["data"]
            self.assertEqual(data[0]["changelog_message"], "own")
            self.assertEqual(data[1]["changelog_message"], "bulk")

    def test_delete_applies_changelog_message(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=True
        ) as mock:
            self.assertTrue(make_endpoint().delete(IDS, changelog_message="bulk"))
            mock.assert_called_with(
                verb="delete",
                data=[{"id": i, "changelog_message": "bulk"} for i in IDS],
            )


class RecordSetChangelogMessageTestCase(unittest.TestCase):
    def test_update_applies_changelog_message(self):
        with patch("pynetbox.core.query.Request._make_call", return_value=[]) as mock:
            make_recordset().update(status="offline", changelog_message="bulk")
            mock.assert_called_with(
                verb="patch",
                data=[
                    {"changelog_message": "bulk", "status": "offline", "id": i}
                    for i in IDS
                ],
            )

    def test_delete_applies_changelog_message(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=True
        ) as mock:
            self.assertTrue(make_recordset().delete(changelog_message="bulk"))
            mock.assert_called_with(
                verb="delete",
                data=[{"id": i, "changelog_message": "bulk"} for i in IDS],
            )
