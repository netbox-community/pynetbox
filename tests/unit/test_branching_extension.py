import unittest
from unittest.mock import patch

import pynetbox
from pynetbox.extensions import BranchingExtension
from pynetbox.extensions.branching import (
    Branches,
    BranchEvents,
    Changes,
)
from pynetbox.models.core import Jobs


def make_api():
    return pynetbox.api(
        "http://localhost:8000",
        token="abc",
        extensions=[BranchingExtension],
    )


class BranchingEndpointResolutionTestCase(unittest.TestCase):
    def test_branches_endpoint_resolves_to_branches_record(self):
        nb = make_api()
        self.assertIs(nb.plugins.branching.branches.return_obj, Branches)

    def test_branch_events_endpoint_resolves(self):
        nb = make_api()
        self.assertIs(nb.plugins.branching.branch_events.return_obj, BranchEvents)

    def test_changes_endpoint_resolves(self):
        nb = make_api()
        self.assertIs(nb.plugins.branching.changes.return_obj, Changes)

    def test_branches_url_slug(self):
        nb = make_api()
        # plugins/branching with underscores in the attribute name
        # should still produce the dashed URL slug.
        self.assertEqual(
            nb.plugins.branching.branches.url,
            "http://localhost:8000/api/plugins/branching/branches",
        )


class BranchActionsTestCase(unittest.TestCase):
    """Cover #710: branch.merge / .sync / .revert / .archive."""

    def _branch(self, nb):
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=[{"id": 1, "name": "feature-branch"}],
        ):
            return nb.plugins.branching.branches.get(1)

    def _patch_make_call(self, return_value):
        """Patch _make_call so call_args captures (self, *args, **kwargs).

        ``autospec=True`` binds the descriptor so the call records the bound
        Request instance as the first positional arg, letting us assert on
        the constructed URL.
        """
        return patch(
            "pynetbox.core.query.Request._make_call",
            autospec=True,
            return_value=return_value,
        )

    def test_merge_posts_to_correct_url_and_returns_job(self):
        nb = make_api()
        branch = self._branch(nb)
        with self._patch_make_call(
            {"id": 42, "name": "Merge Branch", "status": "pending"}
        ) as mock_call:
            job = branch.merge(commit=True)

        self.assertIsInstance(job, Jobs)
        self.assertEqual(job.id, 42)
        request_self = mock_call.call_args.args[0]
        self.assertEqual(mock_call.call_args.kwargs.get("verb"), "post")
        self.assertEqual(
            mock_call.call_args.kwargs.get("data"),
            {"commit": True, "acknowledge_conflicts": False},
        )
        self.assertEqual(
            request_self.url,
            "http://localhost:8000/api/plugins/branching/branches/1/merge/",
        )

    def test_sync_posts_to_correct_url(self):
        nb = make_api()
        branch = self._branch(nb)
        with self._patch_make_call({"id": 7, "name": "Sync Branch"}) as mock_call:
            job = branch.sync(commit=False, acknowledge_conflicts=True)

        self.assertIsInstance(job, Jobs)
        request_self = mock_call.call_args.args[0]
        self.assertEqual(
            mock_call.call_args.kwargs.get("data"),
            {"commit": False, "acknowledge_conflicts": True},
        )
        self.assertTrue(request_self.url.endswith("/branches/1/sync/"))

    def test_revert_posts_to_correct_url(self):
        nb = make_api()
        branch = self._branch(nb)
        with self._patch_make_call({"id": 9, "name": "Revert Branch"}) as mock_call:
            job = branch.revert(commit=True)

        self.assertIsInstance(job, Jobs)
        request_self = mock_call.call_args.args[0]
        self.assertEqual(mock_call.call_args.kwargs.get("data"), {"commit": True})
        self.assertTrue(request_self.url.endswith("/branches/1/revert/"))

    def test_archive_refreshes_branch(self):
        nb = make_api()
        branch = self._branch(nb)
        with self._patch_make_call(
            {"id": 1, "name": "feature-branch", "status": "archived"}
        ) as mock_call:
            result = branch.archive()

        self.assertIs(result, branch)
        self.assertEqual(str(branch.status), "archived")
        request_self = mock_call.call_args.args[0]
        self.assertEqual(mock_call.call_args.kwargs.get("verb"), "post")
        self.assertEqual(mock_call.call_args.kwargs.get("data"), {})
        self.assertTrue(request_self.url.endswith("/branches/1/archive/"))


class ChangeDiffJsonFieldsTestCase(unittest.TestCase):
    """ChangeDiff has several JSONField columns that must round-trip as dicts."""

    def test_json_fields_preserved(self):
        nb = make_api()
        payload = {
            "id": 11,
            "object_type": "dcim.site",
            "object_id": 7,
            "object_repr": "site-1",
            "action": "update",
            "conflicts": ["name", "status"],
            "diff": {"name": {"original": "old", "modified": "new"}},
            "original_data": {"name": "old", "status": "active"},
            "modified_data": {"name": "new", "status": "active"},
            "current_data": {"name": "old", "status": "active"},
        }
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=[payload]
        ):
            change = nb.plugins.branching.changes.get(11)

        self.assertIsInstance(change, Changes)
        self.assertEqual(change.conflicts, ["name", "status"])
        self.assertEqual(
            change.diff, {"name": {"original": "old", "modified": "new"}}
        )
        self.assertEqual(change.original_data, {"name": "old", "status": "active"})
        self.assertEqual(change.modified_data, {"name": "new", "status": "active"})
        self.assertEqual(change.current_data, {"name": "old", "status": "active"})

        # And the dicts survive a serialize() round-trip.
        serialized = change.serialize()
        self.assertEqual(serialized["diff"], payload["diff"])
        self.assertEqual(serialized["original_data"], payload["original_data"])


class BranchingContentTypesTestCase(unittest.TestCase):
    def test_content_types_registered(self):
        nb = make_api()
        self.assertIs(
            nb._content_type_mapper["netbox_branching.branch"], Branches
        )
        self.assertIs(
            nb._content_type_mapper["netbox_branching.changediff"], Changes
        )
