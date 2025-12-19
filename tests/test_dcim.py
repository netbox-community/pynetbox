import unittest
from unittest.mock import patch

import pynetbox

from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.dcim

HEADERS = {"accept": "application/json"}


class Generic:
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "dcim"

        def test_get_all(self):
            with patch(
                "requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = list(getattr(nb, self.name).all())
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={"limit": 0},
                    json=None,
                    headers=HEADERS,
                )

        def test_filter(self):
            with patch(
                "requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = list(getattr(nb, self.name).filter(name="test"))
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={"name": "test", "limit": 0},
                    json=None,
                    headers=HEADERS,
                )

        def test_get(self):
            with patch(
                "requests.sessions.Session.get",
                return_value=Response(
                    fixture="{}/{}.json".format(self.app, self.name[:-1])
                ),
            ) as mock:
                ret = getattr(nb, self.name).get(1)
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret, self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/1/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={},
                    json=None,
                    headers=HEADERS,
                )


class SitesTestCase(Generic.Tests):
    name = "sites"


class RegionsTestCase(Generic.Tests):
    name = "regions"


class SiteGroupsTestCase(Generic.Tests):
    name = "site_groups"


class LocationsTestCase(Generic.Tests):
    name = "locations"


class RackRolesTestCase(Generic.Tests):
    name = "rack_roles"


class RacksTestCase(Generic.Tests):
    name = "racks"


class ManufacturersTestCase(Generic.Tests):
    name = "manufacturers"


class DeviceTypesTestCase(Generic.Tests):
    name = "device_types"


class DeviceRolesTestCase(Generic.Tests):
    name = "device_roles"


class PlatformsTestCase(Generic.Tests):
    name = "platforms"


class DevicesTestCase(Generic.Tests):
    name = "devices"


class InterfacesTestCase(Generic.Tests):
    name = "interfaces"


class ConsolePortsTestCase(Generic.Tests):
    name = "console_ports"


class ConsoleServerPortsTestCase(Generic.Tests):
    name = "console_server_ports"


class PowerPortsTestCase(Generic.Tests):
    name = "power_ports"


class PowerOutletsTestCase(Generic.Tests):
    name = "power_outlets"


class CablesTestCase(Generic.Tests):
    name = "cables"


class ModuleTypesTestCase(Generic.Tests):
    name = "module_types"


class PowerPanelsTestCase(Generic.Tests):
    name = "power_panels"


class PowerFeedsTestCase(Generic.Tests):
    name = "power_feeds"


class InventoryItemsTestCase(Generic.Tests):
    name = "inventory_items"
