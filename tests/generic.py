"""Common Generic test class for all unit tests."""

import unittest
from unittest.mock import patch

import pynetbox

from .util import Response


# Mapping of plural endpoint names to their singular forms
PLURAL_TO_SINGULAR = {
    "addresses": "address",
    "aggregates": "aggregate",
    "cables": "cable",
    "categories": "category",
    "devices": "device",
    "interfaces": "interface",
    "machines": "machine",
    "policies": "policy",
    "prefixes": "prefix",
    "profiles": "profile",
    "ranges": "range",
    "roles": "role",
    "rules": "rule",
    "services": "service",
    "sites": "site",
    "sources": "source",
    "templates": "template",
    "types": "type",
}


class Generic:
    """Generic test class with common test methods for NetBox endpoints."""

    class Tests(unittest.TestCase):
        """Base test class for endpoint testing.

        Subclasses should define:
        - name: endpoint name (e.g., "circuits", "devices")
        - app: API app name (e.g., "circuits", "dcim")
        - nb: API app instance (inherited from module)
        - HEADERS: HTTP headers (inherited from module)
        """

        name = ""
        ret = pynetbox.core.response.Record
        app = ""

        def test_get_all(self):
            # Get nb and HEADERS from the test module
            nb = self.__class__.__module__
            import sys

            module = sys.modules[nb]
            nb_app = module.nb
            headers = module.HEADERS

            with patch(
                "requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = list(getattr(nb_app, self.name).all())
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={"limit": 0},
                    json=None,
                    headers=headers,
                )

        def test_filter(self):
            # Get nb and HEADERS from the test module
            nb = self.__class__.__module__
            import sys

            module = sys.modules[nb]
            nb_app = module.nb
            headers = module.HEADERS

            with patch(
                "requests.sessions.Session.get",
                return_value=Response(fixture="{}/{}.json".format(self.app, self.name)),
            ) as mock:
                ret = list(getattr(nb_app, self.name).filter(name="test"))
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret[0], self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={"name": "test", "limit": 0},
                    json=None,
                    headers=headers,
                )

        def test_get(self):
            # Get nb and HEADERS from the test module
            nb = self.__class__.__module__
            import sys

            module = sys.modules[nb]
            nb_app = module.nb
            headers = module.HEADERS

            # Get singular form from mapping
            singular_name = PLURAL_TO_SINGULAR.get(self.name) or self.name

            with patch(
                "requests.sessions.Session.get",
                return_value=Response(
                    fixture="{}/{}.json".format(self.app, singular_name)
                ),
            ) as mock:
                ret = getattr(nb_app, self.name).get(1)
                self.assertTrue(ret)
                self.assertTrue(isinstance(ret, self.ret))
                mock.assert_called_with(
                    "http://localhost:8000/api/{}/{}/1/".format(
                        self.app, self.name.replace("_", "-")
                    ),
                    params={},
                    json=None,
                    headers=headers,
                )
