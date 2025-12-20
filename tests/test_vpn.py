import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.vpn

HEADERS = {"accept": "application/json"}


class VpnBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "vpn"


class IkePoliciesTestCase(VpnBase):
    name = "ike_policies"


class IkeProposalsTestCase(VpnBase):
    name = "ike_proposals"


class IpsecPoliciesTestCase(VpnBase):
    name = "ipsec_policies"


class IpsecProfilesTestCase(VpnBase):
    name = "ipsec_profiles"


class IpsecProposalsTestCase(VpnBase):
    name = "ipsec_proposals"


class L2vpnTerminationsTestCase(VpnBase):
    name = "l2vpn_terminations"


class L2vpnsTestCase(VpnBase):
    name = "l2vpns"


class TunnelGroupsTestCase(VpnBase):
    name = "tunnel_groups"


class TunnelTerminationsTestCase(VpnBase):
    name = "tunnel_terminations"


class TunnelsTestCase(VpnBase):
    name = "tunnels"
