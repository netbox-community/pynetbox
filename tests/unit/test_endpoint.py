import unittest

import six

from pynetbox.core.endpoint import Endpoint

if six.PY3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock


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
