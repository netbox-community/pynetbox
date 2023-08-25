import unittest
from unittest.mock import Mock

from pynetbox.core.query import Request


class RequestTestCase(unittest.TestCase):
    def test_get_openapi_version_less_than_3_5(self):
        test = Request("http://localhost:8080/api", Mock())
        test.get_version = Mock(return_value="3.4")

        # Mock the HTTP response
        response_mock = Mock()
        response_mock.ok = True
        test.http_session.get.return_value = response_mock

        test.get_openapi()
        test.http_session.get.assert_called_with(
            "http://localhost:8080/api/docs/?format=openapi",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    def test_get_openapi_version_3_5_or_greater(self):
        test = Request("http://localhost:8080/api", Mock())
        test.get_version = Mock(return_value="3.5")

        # Mock the HTTP response
        response_mock = Mock()
        response_mock.ok = True
        test.http_session.get.return_value = response_mock

        test.get_openapi()
        test.http_session.get.assert_called_with(
            "http://localhost:8080/api/schema/",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
