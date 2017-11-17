import unittest
import six

from .util import Response
import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


class ApiTestCase(unittest.TestCase):
    @patch(
        'pynetbox.lib.query.requests.post',
        return_value=Response(fixture='api/get_session_key.json')
    )
    def test_get(self, mock):
        api = pynetbox.api(
            "http://localhost:8000",
            token='abc123',
            private_key_file='tests/fixtures/api/get_session_key.json',
            version='2.0'
        )
        self.assertTrue(api)
