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
    version='2.0'
)

nb = api.virtualization

HEADERS = {
    'accept': 'application/json; version=2.0;'
}


class GenericTest(object):
    name = None
    ret = pynetbox.lib.response.Record
    app = 'virtualization'

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
            mock.assert_called_with(
                'http://localhost:8000/api/{}/{}/1/'.format(
                    self.app,
                    self.name.replace('_', '-')
                ),
                headers=HEADERS,
                verify=True
            )


class ClusterTypesTestCase(unittest.TestCase, GenericTest):
    name = 'cluster_types'


class ClusterGroupsTestCase(unittest.TestCase, GenericTest):
    name = 'cluster_groups'


class ClustersTestCase(unittest.TestCase, GenericTest):
    name = 'clusters'


class VirtualMachinesTestCase(unittest.TestCase, GenericTest):
    name = 'virtual_machines'


class InterfacesTestCase(unittest.TestCase, GenericTest):
    name = 'interfaces'
