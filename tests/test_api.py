import unittest
import six

import pynetbox
from .util import Response

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

host = "http://localhost:8000"

def_kwargs = {
    'token': 'abc123',
    'private_key_file': 'tests/fixtures/api/get_session_key.json',
}

# Keys are app names, values are arbitrarily selected endpoints
# We use dcim and ipam since they have unique app classes
# and circuits because it does not. We don't add other apps/endpoints
# beyond 'circuits' as they all use the same code as each other
endpoints = {
    'dcim': 'devices',
    'ipam': 'prefixes',
    'circuits': 'circuits',
}


class ApiTestCase(unittest.TestCase):

    @patch(
        'pynetbox.core.query.requests.post',
        return_value=Response(fixture='api/get_session_key.json')
    )
    def test_get(self, *_):
        api = pynetbox.api(
            host,
            **def_kwargs
        )
        self.assertTrue(api)

    @patch(
        'pynetbox.core.query.requests.post',
        return_value=Response(fixture='api/get_session_key.json')
    )
    def test_sanitize_url(self, *_):
        api = pynetbox.api(
            'http://localhost:8000/',
            **def_kwargs
        )
        self.assertTrue(api)
        self.assertEqual(api.base_url, 'http://localhost:8000/api')


class ApiArgumentsTestCase(unittest.TestCase):

    @patch(
        'pynetbox.core.query.requests.post',
        return_value=Response(fixture='api/get_session_key.json')
    )
    def common_arguments(self, kwargs, arg, expect, *_):
        '''
        Ensures the api and endpoint instances have ssl_verify set
        as expected
        '''
        api = pynetbox.api(
            host,
            **kwargs
        )
        self.assertIs(getattr(api, arg, "fail"), expect)
        for app, endpoint in endpoints.items():
            ep = getattr(getattr(api, app), endpoint)
            self.assertIs(getattr(ep, arg), expect)

    def test_ssl_verify_default(self):
        self.common_arguments(def_kwargs, 'ssl_verify', True)

    def test_ssl_verify_true(self):
        kwargs = dict(def_kwargs, **{'ssl_verify': True})
        self.common_arguments(kwargs, 'ssl_verify', True)

    def test_ssl_verify_false(self):
        kwargs = dict(def_kwargs, **{'ssl_verify': False})
        self.common_arguments(kwargs, 'ssl_verify', False)

    def test_ssl_verify_string(self):
        kwargs = dict(def_kwargs, **{'ssl_verify': '/path/to/bundle'})
        self.common_arguments(kwargs, 'ssl_verify', '/path/to/bundle')
