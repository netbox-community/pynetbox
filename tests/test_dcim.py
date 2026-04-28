import unittest
from unittest.mock import patch

import pynetbox
from pynetbox.models.ipam import IpAddresses

from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.dcim

HEADERS = {"accept": "application/json"}


class Generic:
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "dcim"

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


class DevicesTestCase(Generic.Tests):
    name = "devices"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="dcim/device.json"),
    )
    def test_oob_ip_attr(self, _):
        device = nb.devices.get(1)
        self.assertIsInstance(device.oob_ip, IpAddresses)
        self.assertEqual(str(device.oob_ip), "192.0.2.1/32")
