"""End-to-end checks that changelog_message reaches the NetBox changelog (#793)."""

import pytest
from packaging import version


@pytest.fixture(autouse=True)
def skip_before_4_4(nb_version):
    if version.parse(str(nb_version)) < version.parse("4.4"):
        pytest.skip("changelog messages require NetBox 4.4+")


def changelog_message(api, obj_id, action):
    """Return the message on the latest changelog entry for a site."""
    changes = list(
        api.core.object_changes.filter(
            changed_object_type="dcim.site",
            changed_object_id=obj_id,
            action=action,
        )
    )
    assert changes, "no {} changelog entry for site {}".format(action, obj_id)
    return max(changes, key=lambda c: c.id).message


def create_sites(api, prefix, count):
    return [
        api.dcim.sites.create(
            name="{}-{}".format(prefix, i), slug="{}-{}".format(prefix, i)
        )
        for i in range(count)
    ]


class TestChangelogMessage:
    def test_create(self, api):
        site = api.dcim.sites.create(
            name="cl-create", slug="cl-create", changelog_message="created"
        )
        try:
            assert changelog_message(api, site.id, "create") == "created"
        finally:
            site.delete()

    def test_save(self, api):
        site = api.dcim.sites.create(name="cl-save", slug="cl-save")
        try:
            site.description = "saved"
            assert site.save(changelog_message="saved")
            assert changelog_message(api, site.id, "update") == "saved"
        finally:
            site.delete()

    def test_update(self, api):
        site = api.dcim.sites.create(name="cl-update", slug="cl-update")
        try:
            assert site.update({"description": "updated"}, changelog_message="updated")
            assert changelog_message(api, site.id, "update") == "updated"
        finally:
            site.delete()

    def test_delete(self, api):
        site = api.dcim.sites.create(name="cl-delete", slug="cl-delete")
        assert site.delete(changelog_message="deleted")
        assert changelog_message(api, site.id, "delete") == "deleted"

    def test_endpoint_bulk_update(self, api):
        sites = create_sites(api, "cl-bulk-update", 2)
        try:
            for site in sites:
                site.description = "bulk updated"
            api.dcim.sites.update(sites, changelog_message="bulk updated")
            for site in sites:
                assert changelog_message(api, site.id, "update") == "bulk updated"
        finally:
            api.dcim.sites.delete(sites)

    def test_recordset_update(self, api):
        sites = create_sites(api, "cl-rs-update", 2)
        try:
            api.dcim.sites.filter(slug=[s.slug for s in sites]).update(
                description="rs updated", changelog_message="rs updated"
            )
            for site in sites:
                assert changelog_message(api, site.id, "update") == "rs updated"
        finally:
            api.dcim.sites.delete(sites)

    def test_endpoint_bulk_delete(self, api):
        sites = create_sites(api, "cl-bulk-delete", 2)
        assert api.dcim.sites.delete(sites, changelog_message="bulk deleted")
        for site in sites:
            assert changelog_message(api, site.id, "delete") == "bulk deleted"

    def test_recordset_delete(self, api):
        sites = create_sites(api, "cl-rs-delete", 2)
        assert api.dcim.sites.filter(slug=[s.slug for s in sites]).delete(
            changelog_message="rs deleted"
        )
        for site in sites:
            assert changelog_message(api, site.id, "delete") == "rs deleted"
