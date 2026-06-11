import pytest
from packaging import version

import pynetbox


@pytest.fixture(scope="module")
def cursor_api(docker_netbox_service):
    """An Api instance configured for cursor pagination (NetBox 4.6+)."""
    nb = pynetbox.api(docker_netbox_service["url"], pagination="cursor")
    nb.create_token("admin", "admin")
    return nb


@pytest.fixture(scope="module")
def prefixes(api):
    """Create enough prefixes to span more than one cursor page."""
    created = [
        api.ipam.prefixes.create(prefix="198.51.100.{}/32".format(i))
        for i in range(5)
    ]
    yield created
    for prefix in created:
        prefix.delete()


class TestCursorPagination:
    def test_cursor_pagination_returns_all_objects(
        self, cursor_api, nb_version, prefixes
    ):
        """Cursor pagination walks every page and yields all objects.

        Gated to NetBox 4.6+, where cursor pagination is available. On older
        versions the client transparently falls back to offset pagination, so
        this end-to-end check of the ``start`` semantics and ``next`` link
        following is only meaningful from 4.6 onward.
        """
        if nb_version < version.parse("4.6"):
            pytest.skip("cursor pagination requires NetBox 4.6+")

        assert cursor_api._effective_pagination() == "cursor"

        # Force a small page size so the result set spans multiple cursor
        # pages and the next-link following is actually exercised.
        results = list(cursor_api.ipam.prefixes.filter(limit=2))
        returned = {str(p.prefix) for p in results}
        for prefix in prefixes:
            assert str(prefix.prefix) in returned

    def test_cursor_pagination_count(self, cursor_api, nb_version, prefixes):
        """len() on a cursor RecordSet refetches the count NetBox omits."""
        if nb_version < version.parse("4.6"):
            pytest.skip("cursor pagination requires NetBox 4.6+")

        record_set = cursor_api.ipam.prefixes.filter(limit=2)
        assert len(record_set) >= len(prefixes)
