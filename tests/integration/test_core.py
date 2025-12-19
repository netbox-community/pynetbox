import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "core"

    def _init_helper(
        self,
        request,
        fixture,
        update_field=None,
        filter_kwargs=None,
        endpoint=None,
        str_repr=None,
    ):
        request.cls.endpoint = endpoint
        request.cls.fixture = fixture
        request.cls.update_field = update_field
        request.cls.filter_kwargs = filter_kwargs
        request.cls.str_repr = str_repr

    def test_create(self):
        assert self.fixture

    def test_str(self):
        if self.str_repr:
            test = str(self.fixture)
            assert test == self.str_repr

    def test_update_fixture(self):
        if self.update_field:
            setattr(self.fixture, self.update_field, "Test Value")
            assert self.fixture.save()

    def test_get_fixture_by_id(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(self.fixture.id)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_get_fixture_by_kwarg(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_filter_fixture(self, api):
        test = list(
            getattr(getattr(api, self.app), self.endpoint).filter(**self.filter_kwargs)
        )[0]
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"


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
            test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
            assert test
