import unittest
from unittest.mock import patch

import pynetbox

from .generic import Generic
from .util import Response

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.users

HEADERS = {"accept": "application/json"}


class UsersBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "users"


class UsersTestCase(UsersBase):
    name = "users"

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="users/user.json"),
    )
    def test_repr(self, _):
        test = nb.users.get(1)
        self.assertEqual(type(test), pynetbox.models.users.Users)
        self.assertEqual(str(test), "user1")


class GroupsTestCase(UsersBase):
    name = "groups"


class PermissionsTestCase(UsersBase):
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

    @patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture="users/permission.json"),
    )
    def test_constraints(self, _):
        permission = nb.permissions.get(1)
        self.assertIsInstance(permission.constraints, list)
        self.assertIsInstance(permission.constraints[0], dict)


class TokensTestCase(UsersBase):
    name = "tokens"


class UnknownModelTestCase(unittest.TestCase):
    """This test validates that an unknown model is returned as Record object
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
