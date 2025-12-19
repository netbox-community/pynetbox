import unittest
from unittest.mock import patch

import pynetbox

from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.extras

HEADERS = {"accept": "application/json"}


class Generic:
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "extras"

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


class TagsTestCase(Generic.Tests):
    name = "tags"


class WebhooksTestCase(Generic.Tests):
    name = "webhooks"


class ConfigContextsTestCase(Generic.Tests):
    name = "config_contexts"


class CustomFieldsTestCase(Generic.Tests):
    name = "custom_fields"
