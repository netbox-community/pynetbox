import unittest
from unittest.mock import patch

import pynetbox

from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.vpn

HEADERS = {"accept": "application/json"}


class Generic:
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "vpn"

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


class IkePoliciesTestCase(Generic.Tests):
    name = "ike_policies"


class IkeProposalsTestCase(Generic.Tests):
    name = "ike_proposals"


class IpsecPoliciesTestCase(Generic.Tests):
    name = "ipsec_policies"


class IpsecProfilesTestCase(Generic.Tests):
    name = "ipsec_profiles"


class IpsecProposalsTestCase(Generic.Tests):
    name = "ipsec_proposals"


class L2vpnTerminationsTestCase(Generic.Tests):
    name = "l2vpn_terminations"


class L2vpnsTestCase(Generic.Tests):
    name = "l2vpns"


class TunnelGroupsTestCase(Generic.Tests):
    name = "tunnel_groups"


class TunnelTerminationsTestCase(Generic.Tests):
    name = "tunnel_terminations"


class TunnelsTestCase(Generic.Tests):
    name = "tunnels"
