import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.ipam

HEADERS = {"accept": "application/json"}


class IpamTests(Generic.Tests):
    app = "ipam"


class AggregatesTestCase(IpamTests):
    name = "aggregates"


class AsnRangesTestCase(IpamTests):
    name = "asn_ranges"


class AsnsTestCase(IpamTests):
    name = "asns"


class FhrpGroupsTestCase(IpamTests):
    name = "fhrp_groups"


class FhrpGroupAssignmentsTestCase(IpamTests):
    name = "fhrp_group_assignments"


class IpAddressesTestCase(IpamTests):
    name = "ip_addresses"


class IpRangesTestCase(IpamTests):
    name = "ip_ranges"


class PrefixesTestCase(IpamTests):
    name = "prefixes"


class RirsTestCase(IpamTests):
    name = "rirs"


class RolesTestCase(IpamTests):
    name = "roles"


class RouteTargetsTestCase(IpamTests):
    name = "route_targets"


class ServiceTemplatesTestCase(IpamTests):
    name = "service_templates"


class ServicesTestCase(IpamTests):
    name = "services"


class VlanGroupsTestCase(IpamTests):
    name = "vlan_groups"


class VlansTestCase(IpamTests):
    name = "vlans"


class VlanTranslationPoliciesTestCase(IpamTests):
    name = "vlan_translation_policies"


class VlanTranslationRulesTestCase(IpamTests):
    name = "vlan_translation_rules"


class VrfsTestCase(IpamTests):
    name = "vrfs"
