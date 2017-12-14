import unittest
import json

import netaddr
import six

from .util import Response
import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


api = pynetbox.api(
    "http://localhost:8000",
    version='2.0'
)

nb = api.ipam

HEADERS = {
    'accept': 'application/json; version=2.0;'
}

POST_HEADERS = {
    'Content-Type': 'application/json; version=2.0;',
    'authorization': 'Token None',
}


class GenericTest(object):
    name = None
    name_singular = None
    ret = pynetbox.lib.response.IPRecord
    app = 'ipam'
    ip_obj_fields = {}

    def test_get_all(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name
            ))
        ) as mock:
            ret = getattr(nb, self.name).all()
            self.assertTrue(ret)
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(isinstance(ret[0], self.ret))
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )

    def test_filter(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name
            ))
        ) as mock:
            ret = getattr(nb, self.name).filter(pk=1)
            self.assertTrue(ret)
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(isinstance(ret[0], self.ret))
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/?pk=1'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )

    def test_get(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name_singular or self.name[:-1]
            ))
        ) as mock:
            ret = getattr(nb, self.name).get(1)
            self.assertTrue(ret)
            self.assertTrue(isinstance(ret, self.ret))
            self.assertTrue(isinstance(dict(ret), dict))
            self.assertTrue(isinstance(str(ret), str))
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/1/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )
            if self.ip_obj_fields:
                for field in self.ip_obj_fields:
                    self.assertTrue(
                        isinstance(getattr(ret, field), netaddr.IPNetwork)
                    )
                    self.assertTrue(netaddr.IPNetwork(dict(ret)[field]))


class PrefixTestCase(unittest.TestCase, GenericTest):
    name = 'prefixes'
    name_singular = 'prefix'
    ip_obj_fields = ['prefix']

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='ipam/prefix.json')
    )
    def test_modify(self, mock):
        ret = nb.prefixes.get(1)
        ret.prefix = '10.1.2.0/24'
        ret_serialized = ret.serialize()
        self.assertTrue(ret_serialized)
        self.assertFalse(ret._compare())
        self.assertEqual(ret_serialized['prefix'], '10.1.2.0/24')
        self.assertTrue(netaddr.IPNetwork(ret_serialized['prefix']))

    @patch(
        'pynetbox.lib.query.requests.get',
        side_effect=[
            Response(fixture='ipam/prefix.json'),
            Response(fixture='ipam/available-ips.json'),
        ]
    )
    def test_get_available_ips(self, mock):
        pfx = nb.prefixes.get(1)
        ret = pfx.available_ips.list()
        mock.assert_called_with(
            'http://localhost:8000/api/ipam/prefixes/1/available-ips/'.format(self.name),
            headers=HEADERS,
            verify=True
        )
        self.assertTrue(ret)
        self.assertEqual(len(ret), 3)

    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='ipam/available-ips-post.json')
    )
    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='ipam/prefix.json'),
    )
    def test_create_available_ips(self, get, post):
        expected_result = {
            'status': 1,
            'description': '',
            'nat_inside': None,
            'role': None,
            'vrf': None,
            'address':
            '10.1.1.1/32',
            'interface': None,
            'id': 1,
            'tenant': None
        }
        create_parms = dict(
            status=2,
        )
        pfx = nb.prefixes.get(1)
        ret = pfx.available_ips.create(create_parms)
        post.assert_called_with(
            'http://localhost:8000/api/ipam/prefixes/1/available-ips/'.format(self.name),
            headers=POST_HEADERS,
            data=json.dumps(create_parms),
            verify=True
        )
        self.assertTrue(ret)
        self.assertEqual(ret, expected_result)

    @patch(
        'pynetbox.lib.query.requests.get',
        side_effect=[
            Response(fixture='ipam/prefix.json'),
            Response(fixture='ipam/available-prefixes.json'),
        ]
    )
    def test_get_available_prefixes(self, mock):
        pfx = nb.prefixes.get(1)
        ret = pfx.available_prefixes.list()
        mock.assert_called_with(
            'http://localhost:8000/api/ipam/prefixes/1/available-prefixes/'.format(self.name),
            headers=HEADERS,
            verify=True
        )
        self.assertTrue(ret)

    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='ipam/available-prefixes-post.json')
    )
    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='ipam/prefix.json'),
    )
    def test_create_available_prefixes(self, get, post):
        create_parms = dict(
            prefix_length=30,
        )
        pfx = nb.prefixes.get(1)
        ret = pfx.available_prefixes.create(create_parms)
        post.assert_called_with(
            'http://localhost:8000/api/ipam/prefixes/1/available-prefixes/'.format(self.name),
            headers=POST_HEADERS,
            data=json.dumps(create_parms),
            verify=True
        )
        self.assertTrue(ret)


class IPAddressTestCase(unittest.TestCase, GenericTest):
    name = 'ip_addresses'
    name_singular = 'ip_address'
    ip_obj_fields = ['address']

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='ipam/ip_address.json')
    )
    def test_modify(self, mock):
        ret = nb.prefixes.get(1)
        ret.description = 'testing'
        ret_serialized = ret.serialize()
        self.assertTrue(ret_serialized)
        self.assertFalse(ret._compare())
        self.assertEqual(ret_serialized['address'], '10.0.255.1/32')
        self.assertEqual(ret_serialized['description'], 'testing')
        self.assertTrue(netaddr.IPNetwork(ret_serialized['address']))


class RoleTestCase(unittest.TestCase, GenericTest):
    name = 'roles'


class RIRTestCase(unittest.TestCase, GenericTest):
    name = 'rirs'


class AggregatesTestCase(unittest.TestCase, GenericTest):
    name = 'aggregates'
    ip_obj_fields = ['prefix']


class VlanTestCase(unittest.TestCase, GenericTest):
    name = 'vlans'


class VlanGroupsTestCase(unittest.TestCase, GenericTest):
    name = 'vlan_groups'


class VRFTestCase(unittest.TestCase, GenericTest):
    name = 'vrfs'


# class ServicesTestCase(unittest.TestCase, GenericTest):
#     name = 'services'
