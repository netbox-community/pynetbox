import unittest
from unittest.mock import patch

import pynetbox

from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.ipam

HEADERS = {"accept": "application/json"}


class Generic:
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "ipam"

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


class AggregatesTestCase(Generic.Tests):
    name = "aggregates"


class AsnRangesTestCase(Generic.Tests):
    name = "asn_ranges"


class AsnsTestCase(Generic.Tests):
    name = "asns"


class FhrpGroupsTestCase(Generic.Tests):
    name = "fhrp_groups"


class FhrpGroupAssignmentsTestCase(Generic.Tests):
    name = "fhrp_group_assignments"


class IpAddressesTestCase(Generic.Tests):
    name = "ip_addresses"


class IpRangesTestCase(Generic.Tests):
    name = "ip_ranges"


class PrefixesTestCase(Generic.Tests):
    name = "prefixes"


class RirsTestCase(Generic.Tests):
    name = "rirs"


class RolesTestCase(Generic.Tests):
    name = "roles"


class RouteTargetsTestCase(Generic.Tests):
    name = "route_targets"


class ServiceTemplatesTestCase(Generic.Tests):
    name = "service_templates"


class ServicesTestCase(Generic.Tests):
    name = "services"


class VlanGroupsTestCase(Generic.Tests):
    name = "vlan_groups"


class VlansTestCase(Generic.Tests):
    name = "vlans"


class VlanTranslationPoliciesTestCase(Generic.Tests):
    name = "vlan_translation_policies"


class VlanTranslationRulesTestCase(Generic.Tests):
    name = "vlan_translation_rules"


class VrfsTestCase(Generic.Tests):
    name = "vrfs"
