import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.vpn

HEADERS = {"accept": "application/json"}


class VpnTests(Generic.Tests):
    app = "vpn"


class IkePoliciesTestCase(VpnTests):
    name = "ike_policies"


class IkeProposalsTestCase(VpnTests):
    name = "ike_proposals"


class IpsecPoliciesTestCase(VpnTests):
    name = "ipsec_policies"


class IpsecProfilesTestCase(VpnTests):
    name = "ipsec_profiles"


class IpsecProposalsTestCase(VpnTests):
    name = "ipsec_proposals"


class L2vpnTerminationsTestCase(VpnTests):
    name = "l2vpn_terminations"


class L2vpnsTestCase(VpnTests):
    name = "l2vpns"


class TunnelGroupsTestCase(VpnTests):
    name = "tunnel_groups"


class TunnelTerminationsTestCase(VpnTests):
    name = "tunnel_terminations"


class TunnelsTestCase(VpnTests):
    name = "tunnels"
