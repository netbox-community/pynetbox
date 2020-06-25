import unittest
import six

from .util import Response
import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

api = pynetbox.api("http://localhost:8000",)

nb = api.circuits

HEADERS = {"accept": "application/json;"}


class Generic(object):
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "circuits"

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


class CircuitsTestCase(Generic.Tests):
    name = "circuits"

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit.json"),
    )
    def test_repr(self, _):
        test = nb.circuits.get(1)
        self.assertEqual(str(test), "123456")


class ProviderTestCase(Generic.Tests):
    name = "providers"


class CircuitTypeTestCase(Generic.Tests):
    name = "circuit_types"


class CircuitTerminationsTestCase(Generic.Tests):
    name = "circuit_terminations"

    @patch(
        "pynetbox.core.query.requests.sessions.Session.get",
        return_value=Response(fixture="circuits/circuit_termination.json"),
    )
    def test_repr(self, _):
        test = nb.circuit_terminations.get(1)
        self.assertEqual(str(test), "123456")
