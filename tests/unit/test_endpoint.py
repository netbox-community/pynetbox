import unittest

import six

from pynetbox.core.endpoint import Endpoint

if six.PY3:
    from unittest.mock import patch, Mock, call
else:
    from mock import patch, Mock, call


class EndPointTestCase(unittest.TestCase):

    def test_filter(self):
        with patch(
            "pynetbox.core.query.Request.get", return_value=Mock()
        ) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            mock.return_value = [{'id': 123}, {'id': 321}]
            test_obj = Endpoint(api, app, "test")
            test = test_obj.filter(test="test")
            self.assertEqual(len(test), 2)

    def test_filter_empty_kwargs(self):

        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="test")
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ValueError) as _:
            test_obj.filter()

    def test_filter_reserved_kwargs(self):

        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="test")
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ValueError) as _:
            test_obj.filter(id=1)

    def test_count(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value={"count": 42}
        ) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock()
            app.name = "test-app"
            expected_call = call('http://localhost:8000/api/test-app/test-endpoint/?test_filter=test&limit=1')
            test_obj = Endpoint(api, app, "test_endpoint")
            test = test_obj.count(test_filter="test")
            self.assertEqual(test, 42)
            self.assertEqual(mock.call_args, expected_call)

    def test_count_args(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value={"count": 42}
        ) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock()
            app.name = "test-app"
            expected_call = call('http://localhost:8000/api/test-app/test-endpoint/?q=test&limit=1')
            test_obj = Endpoint(api, app, "test_endpoint")
            test = test_obj.count("test")
            self.assertEqual(test, 42)
            self.assertEqual(mock.call_args, expected_call)

    def test_count_no_args(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value={"count": 42}
        ) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock()
            app.name = "test-app"
            expected_call = call('http://localhost:8000/api/test-app/test-endpoint/?limit=1')
            test_obj = Endpoint(api, app, "test_endpoint")
            test = test_obj.count()
            self.assertEqual(test, 42)
            self.assertEqual(mock.call_args, expected_call)
