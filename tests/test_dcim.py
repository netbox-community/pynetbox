import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.dcim

HEADERS = {"accept": "application/json"}


class DcimTests(Generic.Tests):
    app = "dcim"


class SitesTestCase(DcimTests):
    name = "sites"


class RegionsTestCase(DcimTests):
    name = "regions"


class SiteGroupsTestCase(DcimTests):
    name = "site_groups"


class LocationsTestCase(DcimTests):
    name = "locations"


class RackRolesTestCase(DcimTests):
    name = "rack_roles"


class RacksTestCase(DcimTests):
    name = "racks"


class ManufacturersTestCase(DcimTests):
    name = "manufacturers"


class DeviceTypesTestCase(DcimTests):
    name = "device_types"


class DeviceRolesTestCase(DcimTests):
    name = "device_roles"


class PlatformsTestCase(DcimTests):
    name = "platforms"


class DevicesTestCase(DcimTests):
    name = "devices"


class InterfacesTestCase(DcimTests):
    name = "interfaces"


class ConsolePortsTestCase(DcimTests):
    name = "console_ports"


class ConsoleServerPortsTestCase(DcimTests):
    name = "console_server_ports"


class PowerPortsTestCase(DcimTests):
    name = "power_ports"


class PowerOutletsTestCase(DcimTests):
    name = "power_outlets"


class CablesTestCase(DcimTests):
    name = "cables"


class ModuleTypesTestCase(DcimTests):
    name = "module_types"


class PowerPanelsTestCase(DcimTests):
    name = "power_panels"


class PowerFeedsTestCase(DcimTests):
    name = "power_feeds"


class InventoryItemsTestCase(DcimTests):
    name = "inventory_items"
