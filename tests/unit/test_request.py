import unittest

import six

from pynetbox.core.query import Request

if six.PY3:
    from unittest.mock import Mock
else:
    from mock import Mock


class RequestTestCase(unittest.TestCase):
    def test_get_openapi(self):
        test = Request("http://localhost:8080/api", Mock())
        test.get_openapi()
        test.http_session.get.assert_called_with(
            "http://localhost:8080/api/docs/?format=openapi",
            headers={"Content-Type": "application/json;"},
        )
