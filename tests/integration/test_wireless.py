import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "wireless"

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


class TestWirelessLANGroup(BaseTest):
    @pytest.fixture(scope="class")
    def wireless_lan_group(self, api):
        ret = api.wireless.wireless_lan_groups.create(
            name="test-wlan-group", slug="test-wlan-group"
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, wireless_lan_group):
        self._init_helper(
            request,
            wireless_lan_group,
            filter_kwargs={"name": "test-wlan-group"},
            update_field="description",
            endpoint="wireless_lan_groups",
        )


class TestWirelessLAN(BaseTest):
    @pytest.fixture(scope="class")
    def wireless_lan(self, api):
        ret = api.wireless.wireless_lans.create(ssid="test-ssid")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, wireless_lan):
        self._init_helper(
            request,
            wireless_lan,
            filter_kwargs={"ssid": "test-ssid"},
            update_field="description",
            endpoint="wireless_lans",
        )
