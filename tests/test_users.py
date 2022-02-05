import unittest
import six

import pynetbox
from .util import Response

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


api = pynetbox.api("http://localhost:8000",)

nb = api.users

HEADERS = {"accept": "application/json;"}


class Generic(object):
    class Tests(unittest.TestCase):
        name = ""
        ret = pynetbox.core.response.Record
        app = "users"

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


class UsersTestCase(Generic.Tests):
    name = "users"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="users/user.json"),
    )
    def test_repr(self, _):
        test = nb.users.get(1)
        self.assertEqual(type(test), pynetbox.models.users.Users)
        self.assertEqual(str(test), "user1")


class GroupsTestCase(Generic.Tests):
    name = "groups"


class PermissionsTestCase(Generic.Tests):
    name = "permissions"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="users/permission.json"),
    )
    def test_username(self, _):
        permission = nb.permissions.get(1)
        self.assertEqual(len(permission.users), 1)
        user = permission.users[0]
        self.assertEqual(str(user), "user1")


class UnknownModelTestCase(unittest.TestCase):
    """ This test validates that an unknown model is returned as Record object
    and that the __str__() method correctly uses the 'display' field of the
    object (introduced as a standard field in NetBox 2.11.0).
    """

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="users/unknown_model.json"),
    )
    def test_unknown_model(self, _):
        unknown_obj = nb.unknown_model.get(1)
        self.assertEqual(type(unknown_obj), pynetbox.core.response.Record)
        self.assertEqual(str(unknown_obj), "Unknown object")
