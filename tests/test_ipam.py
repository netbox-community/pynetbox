import unittest
import json

import six

import pynetbox
from .util import Response

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


api = pynetbox.api("http://localhost:8000", token="abc123",)

nb = api.ipam

HEADERS = {
    "accept": "application/json;",
    "authorization": "Token abc123",
}

POST_HEADERS = {
    "Content-Type": "application/json;",
    "authorization": "Token abc123",
}


class Generic(object):
    class Tests(unittest.TestCase):
        name = ""
        name_singular = None
        ret = pynetbox.core.response.Record
        app = "ipam"

        def test_get_all(self):
            with patch(
                "pynetbox.core.query.requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = getattr(nb, self.name).all()
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret, list))
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={},
                    json=None,
                    headers=HEADERS,
                )

        def test_filter(self):
            with patch(
                "pynetbox.core.query.requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = getattr(nb, self.name).filter(name="test")
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret, list))
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={"name": "test"},
                    json=None,
                    headers=HEADERS,
                )

        def test_get(self):
            with patch(
                "pynetbox.core.query.requests.sessions.Session.get",
                return_value=Response(
                    fixture="{}/{}.json".format(
                        self.app, self.name_singular or self.name[:-1]
                    )
                ),
            ) as mock:
                ret = getattr(nb, self.name).get(1)
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret, self.ret))
                self.assertTrue(isinstance(dict(ret), dict))
                self.assertTrue(isinstance(str(ret), str))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/1/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={},
                    json=None,
                    headers=HEADERS,
                )


class PrefixTestCase(Generic.Tests):
    name = "prefixes"
    name_singular = "prefix"

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="ipam/prefix.json"),
    )
    def test_modify(self, *_):
        ret = nb.prefixes.get(1)
        ret.prefix = "10.1.2.0/24"
        ret_serialized = ret.serialize()
        self.assertTrue(ret_serialized)
        self.assertEqual(ret._diff(), {"prefix"})
        self.assertEqual(ret_serialized["prefix"], "10.1.2.0/24")

    @patch(
        "pynetbox.core.query.requests.sessions.Session.put",
        return_value=Response(fixture="ipam/prefix.json"),
    )
    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="ipam/prefix.json"),
    )
    def test_idempotence(self, *_):
        ret = nb.prefixes.get(1)
        test = ret.save()
        self.assertFalse(test)

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        side_effect=[
            Response(fixture="ipam/prefix.json"),
            Response(fixture="ipam/available-ips.json"),
        ],
    )
    def test_get_available_ips(self, mock):
        pfx = nb.prefixes.get(1)
        ret = pfx.available_ips.list()
        mock.assert_called_with(
            "http://localhost:8000/api/ipam/prefixes/1/available-ips/",
            params={},
            json=None,
            headers=HEADERS,
        )
        self.assertTrue(ret)
        self.assertEqual(len(ret), 3)

    @patch(
        "pynetbox.core.query.requests.sessions.Session.post",
        return_value=Response(fixture="ipam/available-ips-post.json"),
    )
    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="ipam/prefix.json"),
    )
    def test_create_available_ips(self, _, post):
        create_parms = dict(status=2,)
        pfx = nb.prefixes.get(1)
        ret = pfx.available_ips.create(create_parms)
        post.assert_called_with(
            "http://localhost:8000/api/ipam/prefixes/1/available-ips/",
            params={},
            headers=POST_HEADERS,
            json=create_parms,
        )
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret, pynetbox.models.ipam.IpAddresses))

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        side_effect=[
            Response(fixture="ipam/prefix.json"),
            Response(fixture="ipam/available-prefixes.json"),
        ],
    )
    def test_get_available_prefixes(self, mock):
        pfx = nb.prefixes.get(1)
        ret = pfx.available_prefixes.list()
        mock.assert_called_with(
            "http://localhost:8000/api/ipam/prefixes/1/available-prefixes/",
            params={},
            json=None,
            headers=HEADERS,
        )
        self.assertTrue(ret)

    @patch(
        "pynetbox.core.query.requests.sessions.Session.post",
        return_value=Response(fixture="ipam/available-prefixes-post.json"),
    )
    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="ipam/prefix.json"),
    )
    def test_create_available_prefixes(self, _, post):
        create_parms = dict(prefix_length=30,)
        pfx = nb.prefixes.get(1)
        ret = pfx.available_prefixes.create(create_parms)
        post.assert_called_with(
            "http://localhost:8000/api/ipam/prefixes/1/available-prefixes/",
            params={},
            headers=POST_HEADERS,
            json=create_parms,
        )
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret[0], pynetbox.models.ipam.Prefixes))


class IPAddressTestCase(Generic.Tests):
    name = "ip_addresses"
    name_singular = "ip_address"

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="ipam/ip_address.json"),
    )
    def test_modify(self, *_):
        ret = nb.prefixes.get(1)
        ret.description = "testing"
        ret_serialized = ret.serialize()
        self.assertTrue(ret_serialized)
        self.assertEqual(ret._diff(), {"description"})
        self.assertEqual(ret_serialized["address"], "10.0.255.1/32")
        self.assertEqual(ret_serialized["description"], "testing")


class RoleTestCase(Generic.Tests):
    name = "roles"


class RIRTestCase(Generic.Tests):
    name = "rirs"


class AggregatesTestCase(Generic.Tests):
    name = "aggregates"


class VlanTestCase(Generic.Tests):
    name = "vlans"

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        side_effect=[
            Response(fixture="ipam/vlan.json"),
            Response(fixture="dcim/interface.json"),
        ],
    )
    def test_vlan_in_interface(self, mock):
        vlan = nb.vlans.get(3)
        interface = api.dcim.interfaces.get(1)
        mock.assert_called_with(
            "http://localhost:8000/api/dcim/interfaces/1/",
            params={},
            json=None,
            headers=HEADERS,
        )
        self.assertEqual(vlan.vid, interface.tagged_vlans[0].vid)
        self.assertEqual(vlan.id, interface.tagged_vlans[0].id)
        self.assertTrue(vlan in interface.tagged_vlans)


class VlanGroupsTestCase(Generic.Tests):
    name = "vlan_groups"


class VRFTestCase(Generic.Tests):
    name = "vrfs"


# class ServicesTestCase(Generic.Tests):
#     name = 'services'
