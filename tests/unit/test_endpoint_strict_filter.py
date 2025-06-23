import unittest
from unittest.mock import Mock
from tests.util import openapi_mock

from pynetbox.core.endpoint import Endpoint
from pynetbox import ParameterValidationError


class StrictFilterTestCase(unittest.TestCase):

    def test_filter_strict_valid_kwargs(self):
        api = Mock(
            base_url="http://localhost:8000/api",
            strict_filters=True,
            openapi=openapi_mock,
        )
        app = Mock(name="test")
        app.name = "test"
        test_obj = Endpoint(api, app, "test")
        test_obj.filter(test="test")

    def test_filter_strict_invalid_kwarg(self):
        api = Mock(
            base_url="http://localhost:8000/api",
            strict_filters=True,
            openapi=openapi_mock,
        )
        app = Mock(name="test")
        app.name = "test"
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ParameterValidationError):
            test_obj.filter(very_invalid_kwarg="test")

    def test_filter_strict_per_request_disable_invalid_kwarg(self):
        api = Mock(
            base_url="http://localhost:8000/api",
            strict_filters=True,  # Enable globally
            openapi=openapi_mock,
        )
        app = Mock(name="test")
        app.name = "test"
        test_obj = Endpoint(api, app, "test")
        # Disable strict_filters only for this specific request
        test_obj.filter(very_invalid_kwarg="test", strict_filters=False)

    def test_filter_strict_per_request_enable_invalid_kwarg(self):
        api = Mock(
            base_url="http://localhost:8000/api",
            strict_filters=False,  # Disable globally
            openapi=openapi_mock,
        )
        app = Mock(name="test")
        app.name = "test"
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ParameterValidationError):
            # Enable strict_filters only for this specific request
            test_obj.filter(very_invalid_kwarg="test", strict_filters=True)
