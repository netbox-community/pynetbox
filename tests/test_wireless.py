import pynetbox

from .generic import Generic

api = pynetbox.api("http://localhost:8000")

nb = api.wireless

HEADERS = {"accept": "application/json"}


class WirelessTests(Generic.Tests):
    app = "wireless"


class WirelessLanGroupsTestCase(WirelessTests):
    name = "wireless_lan_groups"


class WirelessLansTestCase(WirelessTests):
    name = "wireless_lans"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="wireless/wireless_lan.json"),
    )
    def test_repr(self, _):
        wireless_lan_obj = nb_app.wireless_lans.get(1)
        self.assertEqual(type(wireless_lan_obj), pynetbox.models.wireless.WirelessLans)
        self.assertEqual(str(wireless_lan_obj), "SSID 1")


class WirelessLinksTestCase(WirelessTests):
    name = "wireless_links"
