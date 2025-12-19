import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "wireless"


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
