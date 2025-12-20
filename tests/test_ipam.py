import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.ipam

HEADERS = {"accept": "application/json"}


class IpamBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "ipam"


class AggregatesTestCase(IpamBase):
    name = "aggregates"


class AsnRangesTestCase(IpamBase):
    name = "asn_ranges"


class AsnsTestCase(IpamBase):
    name = "asns"


class FhrpGroupsTestCase(IpamBase):
    name = "fhrp_groups"


class FhrpGroupAssignmentsTestCase(IpamBase):
    name = "fhrp_group_assignments"


class IpAddressesTestCase(IpamBase):
    name = "ip_addresses"


class IpRangesTestCase(IpamBase):
    name = "ip_ranges"


class PrefixesTestCase(IpamBase):
    name = "prefixes"


class RirsTestCase(IpamBase):
    name = "rirs"


class RolesTestCase(IpamBase):
    name = "roles"


class RouteTargetsTestCase(IpamBase):
    name = "route_targets"


class ServiceTemplatesTestCase(IpamBase):
    name = "service_templates"


class ServicesTestCase(IpamBase):
    name = "services"


class VlanGroupsTestCase(IpamBase):
    name = "vlan_groups"


class VlansTestCase(IpamBase):
    name = "vlans"


class VlanTranslationPoliciesTestCase(IpamBase):
    name = "vlan_translation_policies"


class VlanTranslationRulesTestCase(IpamBase):
    name = "vlan_translation_rules"


class VrfsTestCase(IpamBase):
    name = "vrfs"
