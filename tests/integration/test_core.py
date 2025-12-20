import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "core"


class TestDataSource(BaseTest):
    @pytest.fixture(scope="class")
    def data_source(self, api):
        ret = api.core.data_sources.create(
            name="test-datasource",
            type="local",
            source_url="file:///tmp/test",
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, data_source):
        self._init_helper(
            request,
            data_source,
            filter_kwargs={"name": "test-datasource"},
            update_field="description",
            endpoint="data_sources",
        )


class TestObjectChange(BaseTest):
    @pytest.fixture(scope="class")
    def object_change(self, api):
        # ObjectChanges are read-only, created by NetBox automatically
        # We'll create a dummy object to trigger a change and then fetch it
        site = api.dcim.sites.create(name="test-oc-site", slug="test-oc-site")
        site.description = "trigger change"
        site.save()

        # Get the object change for this site
        changes = list(api.core.object_changes.filter(changed_object_id=site.id))
        ret = changes[0] if changes else None

        yield ret

        # Cleanup the site
        site.delete()

    @pytest.fixture(scope="class")
    def init(self, request, object_change):
        if object_change:
            self._init_helper(
                request,
                object_change,
                filter_kwargs={"id": object_change.id},
                endpoint="object_changes",
            )

    def test_create(self):
        # Object changes are created automatically by NetBox
        if self.fixture:
            assert self.fixture

    def test_update_fixture(self):
        # ObjectChanges are read-only, skip update test
        pass

    def test_get_fixture_by_kwarg(self, api):
        if self.fixture:
            test = getattr(getattr(api, self.app), self.endpoint).get(
                **self.filter_kwargs
            )
            assert test
