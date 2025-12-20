from unittest.mock import patch

import pynetbox

from .generic import Generic
from .util import Response

api = pynetbox.api("http://localhost:8000")

nb = api.wireless

HEADERS = {"accept": "application/json"}


class WirelessBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "wireless"


class WirelessLanGroupsTestCase(WirelessBase):
    name = "wireless_lan_groups"


class WirelessLansTestCase(WirelessBase):
    name = "wireless_lans"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="wireless/wireless_lan.json"),
    )
    def test_repr(self, _):
        wireless_lan_obj = nb.wireless_lans.get(1)
        self.assertEqual(type(wireless_lan_obj), pynetbox.models.wireless.WirelessLans)
        self.assertEqual(str(wireless_lan_obj), "SSID 1")


class WirelessLinksTestCase(WirelessBase):
    name = "wireless_links"
