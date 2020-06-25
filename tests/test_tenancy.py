import unittest
import six

import pynetbox
from .util import Response

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


api = pynetbox.api("http://localhost:8000",)

nb = api.tenancy

HEADERS = {"accept": "application/json;"}


class Generic(object):
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "tenancy"

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


class TenantsTestCase(Generic.Tests):
    name = "tenants"


class TenantGroupsTestCase(Generic.Tests):
    name = "tenant_groups"
