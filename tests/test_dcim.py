import unittest
import six

from .util import Response
import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


api = pynetbox.api(
    "http://localhost:8000",
    version='2.0',
)

nb = api.dcim

HEADERS = {
    'accept': 'application/json; version=2.0;',
}

AUTH_HEADERS = {
    'accept': 'application/json; version=2.0;',
    'authorization': 'Token None',
}


class GenericTest(object):
    name = None
    ret = pynetbox.lib.response.Record
    app = 'dcim'

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
                self.name[:-1]
            ))
        ) as mock:
            ret = getattr(nb, self.name).get(1)
            self.assertTrue(ret)
            self.assertTrue(isinstance(ret, self.ret))
            self.assertTrue(isinstance(str(ret), str))
            self.assertTrue(isinstance(dict(ret), dict))
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/1/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )

    def test_delete(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name[:-1]
            ))
        ) as mock, patch('pynetbox.lib.query.requests.delete') as delete:
            ret = getattr(nb, self.name).get(1)
            self.assertTrue(ret.delete())
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/1/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )
            delete.assert_called_with(
                'http://localhost:8000/api/{}/{}/1/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=AUTH_HEADERS,
                verify=True
            )

    def test_compare(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name[:-1]
            ))
        ):
            ret = getattr(nb, self.name).get(1)
            self.assertTrue(ret)
            self.assertTrue(ret._compare())

    def test_serialize(self):
        with patch(
            'pynetbox.lib.query.requests.get',
            return_value=Response(fixture='{}/{}.json'.format(
                self.app,
                self.name[:-1]
            ))
        ):
            ret = getattr(nb, self.name).get(1)
            self.assertTrue(ret)
            self.assertTrue(ret.serialize())


class DeviceTestCase(unittest.TestCase, GenericTest):
    name = 'devices'

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/device.json')
    )
    def test_get(self, mock):
        ret = getattr(nb, self.name).get(1)
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret, self.ret))
        self.assertTrue(isinstance(ret.primary_ip, pynetbox.ipam.IpAddresses))
        self.assertTrue(isinstance(ret.primary_ip4, pynetbox.ipam.IpAddresses))
        mock.assert_called_with(
            'http://localhost:8000/api/{}/{}/1/'.format(
                self.app,
                self.name.replace('_', '-')
            ),
            headers=HEADERS,
            verify=True
        )

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/devices.json')
    )
    def test_multi_filter(self, mock):
        ret = getattr(nb, self.name).filter(role=['test', 'test1'], site='TEST#1')
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret, list))
        self.assertTrue(isinstance(ret[0], self.ret))
        mock.assert_called_with(
            'http://localhost:8000/api/{}/{}/?role=test&role=test1&site=TEST%231'.format(
                self.app,
                self.name.replace('_', '-')
            ),
            headers=HEADERS,
            verify=True
        )

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/device.json')
    )
    def test_modify(self, mock):
        ret = nb.devices.get(1)
        ret.serial = '123123123123'
        ret_serialized = ret.serialize()
        self.assertTrue(ret_serialized)
        self.assertFalse(ret._compare())
        self.assertEqual(ret_serialized['serial'], '123123123123')

    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='dcim/device.json')
    )
    def test_create(self, mock):
        data = {
            'name': 'test-device',
            'site': 1,
            'device_type': 1,
            'device_role': 1,
        }
        ret = nb.devices.create(**data)
        self.assertTrue(ret)

    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='dcim/device_bulk_create.json')
    )
    def test_create_device_bulk(self, mock):
        data = [
            {
                'name': 'test-device',
                'site': 1,
                'device_type': 1,
                'device_role': 1,
            },
            {
                'name': 'test-device1',
                'site': 1,
                'device_type': 1,
                'device_role': 1,
            },
        ]
        ret = nb.devices.create(data)
        self.assertTrue(ret)
        self.assertTrue(len(ret), 2)

    @patch(
        'pynetbox.lib.query.requests.get',
        side_effect=[
            Response(fixture='dcim/device.json'),
            Response(fixture='dcim/rack.json'),
        ]
    )
    def test_get_recurse(self, mock):
        '''Test that automatic recursion works, and that nested items
        are converted to Response() objects.
        '''
        ret = getattr(nb, self.name).get(1)
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret, self.ret))
        self.assertTrue(isinstance(
            ret.rack.role,
            self.ret
        ))

    @patch(
        'pynetbox.lib.query.requests.get',
        side_effect=[
            Response(fixture='dcim/device.json'),
            Response(fixture='dcim/napalm.json'),
        ]
    )
    def test_get_napalm(self, mock):
        test = nb.devices.get(1)
        ret = test.napalm.list(method='get_facts')
        mock.assert_called_with(
            'http://localhost:8000/api/dcim/devices/1/napalm/?method=get_facts',
            headers=HEADERS,
            verify=True,
        )
        self.assertTrue(ret)
        self.assertTrue(ret['get_facts'])


class SiteTestCase(unittest.TestCase, GenericTest):
    name = 'sites'

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/site.json')
    )
    def test_modify_custom(self, mock):
        '''Test modifying a custom field.
        '''
        ret = getattr(nb, self.name).get(1)
        ret.custom_fields['test_custom'] = "Testing"
        self.assertFalse(ret._compare())
        self.assertTrue(ret.serialize())
        self.assertEqual(
            ret.custom_fields['test_custom'], 'Testing'
        )

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/site.json')
    )
    def test_custom_selection_serializer(self, _):
        '''Tests serializer with custom selection fields.
        '''
        ret = getattr(nb, self.name).get(1)
        ret.custom_fields['test_custom'] = "Testing"
        test = ret.serialize()
        from pprint import pprint
        pprint(test)
        self.assertEqual(
            test['custom_fields']['test_selection'],
            2
        )

    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='dcim/site.json')
    )
    def test_create(self, mock):
        data = {
            'name': 'TEST1',
            'custom_fields': {
                'test_custom': 'Testing'
            }
        }
        ret = nb.sites.create(**data)
        self.assertTrue(ret)


class InterfaceTestCase(unittest.TestCase, GenericTest):
    name = 'interfaces'

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/interface.json')
    )
    def test_modify(self, mock):
        ret = nb.interfaces.get(1)
        ret.description = 'Testing'
        ret_serialized = ret.serialize()
        self.assertTrue(ret)
        self.assertEqual(ret_serialized['description'], 'Testing')
        self.assertEqual(ret_serialized['form_factor'], 1400)

    @patch(
        'pynetbox.lib.query.requests.get',
        return_value=Response(fixture='dcim/interface.json')
    )
    def test_modify_connected_iface(self, mock):
        new_iface = dict(
            status=True,
            interface=2
        )
        ret = nb.interfaces.get(1)
        ret.interface_connection = new_iface
        self.assertEqual(
            ret.serialize()['interface_connection'],
            new_iface
        )

    @patch(
        'pynetbox.lib.query.requests.get',
        side_effect=[
            Response(fixture='dcim/{}.json'.format(name + '_1')),
            Response(fixture='dcim/{}.json'.format(name + '_2')),
        ]
    )
    def test_get_all(self, mock):
        ret = getattr(nb, self.name).all()
        self.assertTrue(ret)
        self.assertTrue(isinstance(ret, list))
        self.assertTrue(isinstance(ret[0], self.ret))
        self.assertEqual(len(ret), 71)
        mock.assert_called_with(
            'http://localhost:8000/api/dcim/interfaces/?limit=221&offset=50'.format(self.name),
            headers=HEADERS,
            verify=True
        )


class RackTestCase(unittest.TestCase, GenericTest):
    name = 'racks'


class RackRoleTestCase(unittest.TestCase, GenericTest):
    name = 'rack_roles'


class RegionTestCase(unittest.TestCase, GenericTest):
    name = 'regions'


class RackGroupsTestCase(unittest.TestCase, GenericTest):
    name = 'rack_groups'


class RackReservationsTestCase(unittest.TestCase, GenericTest):
    name = 'rack_reservations'


class ManufacturersTestCase(unittest.TestCase, GenericTest):
    name = 'manufacturers'


class DeviceTypeTestCase(unittest.TestCase, GenericTest):
    name = 'device_types'


class ConsolePortTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'console_port_templates'


class ConsoleServerPortTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'console_server_port_templates'


class PowerPortTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'power_port_templates'


class PowerOutletTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'power_outlet_templates'


class InterfaceTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'interface_templates'


class DeviceBayTemplateTestCase(unittest.TestCase, GenericTest):
    name = 'device_bay_templates'


class DeviceRolesTestCase(unittest.TestCase, GenericTest):
    name = 'device_roles'


class PlatformsTestCase(unittest.TestCase, GenericTest):
    name = 'platforms'


class ConsolePortsTestCase(unittest.TestCase, GenericTest):
    name = 'console_ports'


class ConsoleServerPortsTestCase(unittest.TestCase, GenericTest):
    name = 'console_server_ports'


class PowerPortsTestCase(unittest.TestCase, GenericTest):
    name = 'power_ports'


class PowerOutletsTestCase(unittest.TestCase, GenericTest):
    name = 'power_outlets'


class DeviceBaysTestCase(unittest.TestCase, GenericTest):
    name = 'device_bays'


# class InventoryItemsTestCase(unittest.TestCase, GenericTest):
#     name = 'inventory_items'


class InterfaceConnectionsTestCase(unittest.TestCase, GenericTest):
    name = 'interface_connections'


# class ConnectedDevicesTestCase(unittest.TestCase, GenericTest):
#     name = 'connected_device'


class VirtualChassisTestCase(unittest.TestCase, GenericTest):
    name = 'virtual_chassis_devices'
