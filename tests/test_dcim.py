import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.dcim

HEADERS = {"accept": "application/json"}


class DcimBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "dcim"


class SitesTestCase(DcimBase):
    name = "sites"


class RegionsTestCase(DcimBase):
    name = "regions"


class SiteGroupsTestCase(DcimBase):
    name = "site_groups"


class LocationsTestCase(DcimBase):
    name = "locations"


class RackRolesTestCase(DcimBase):
    name = "rack_roles"


class RacksTestCase(DcimBase):
    name = "racks"


class ManufacturersTestCase(DcimBase):
    name = "manufacturers"


class DeviceTypesTestCase(DcimBase):
    name = "device_types"


class DeviceRolesTestCase(DcimBase):
    name = "device_roles"


class PlatformsTestCase(DcimBase):
    name = "platforms"


class DevicesTestCase(DcimBase):
    name = "devices"


class InterfacesTestCase(DcimBase):
    name = "interfaces"


class ConsolePortsTestCase(DcimBase):
    name = "console_ports"


class ConsoleServerPortsTestCase(DcimBase):
    name = "console_server_ports"


class PowerPortsTestCase(DcimBase):
    name = "power_ports"


class PowerOutletsTestCase(DcimBase):
    name = "power_outlets"


class CablesTestCase(DcimBase):
    name = "cables"


class ModuleTypesTestCase(DcimBase):
    name = "module_types"


class PowerPanelsTestCase(DcimBase):
    name = "power_panels"


class PowerFeedsTestCase(DcimBase):
    name = "power_feeds"


class InventoryItemsTestCase(DcimBase):
    name = "inventory_items"
