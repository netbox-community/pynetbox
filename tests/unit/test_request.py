import unittest
from unittest.mock import Mock

from pynetbox.core.query import Request


class RequestTestCase(unittest.TestCase):
    def test_get_openapi(self):
        test = Request("http://localhost:8080/api", Mock())
        test.get_openapi()
        test.http_session.get.assert_called_with(
            "http://localhost:8080/api/docs/?format=openapi",
            headers={"Content-Type": "application/json;"},
        )
