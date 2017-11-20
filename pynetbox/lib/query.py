'''
(c) 2017 DigitalOcean

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import json
from six.moves.urllib.parse import urlencode

import requests


class RequestError(Exception):
    """Basic Request Exception

    More detailed exception that returns the requests object. Along
    with some attributes with specific details from the requests
    object.
    """
    def __init__(self, message):
        req = message
        message = "The request failed with code {} {}".format(
            req.status_code,
            req.reason
        )
        super(RequestError, self).__init__(message)
        self.req = req
        self.request_body = req.request.body
        self.url = req.url
        self.error = req.text


class Request(object):
    """Creates requests to the Netbox API

    Responsible for building the url and making the HTTP(S) requests to
    Netbox's API

    :param base: (str) Base URL passed in api() instantiation.
    :param filters: (dict, optional) contains key/value pairs that
        correlate to the filters a given endpoint accepts.
        In (e.g. /api/dcim/devices/?name='test') 'name': 'test'
        would be in the filters dict.
    :param private_key: (str, optional) The user's private key as a
        string.
    """

    def __init__(self, base=None, filters=None, key=None, token=None,
                 private_key=None, version=None, session_key=None):
        """
        Instantiates a new Request object

        Args:
            base (string): Base URL passed in api() instantiation.
            filters (dict, optional): contains key/value pairs that
                correlate to the filters a given endpoint accepts.
                In (e.g. /api/dcim/devices/?name='test') 'name': 'test'
                would be in the filters dict.
            key (int, optional): database id of the item being queried.
            private_key (string, optional): The user's private key as a
                string.
        """
        self.base = base
        self.filters = filters
        self.key = key
        self.token = token
        self.private_key = private_key
        self.version = version
        self.session_key = session_key

    def get_version(self):
        """Query the netbox API for its API-Version.

        Queries the API root for the *API-Verion* header.

        :returns: String containing version.
        """
        ret = requests.get(
            "{}/".format(self.base)
        ).headers.get('API-Version', '1.0')
        setattr(self, 'version', ret)
        return ret

    def get_session_key(self):
        """Requests session key

        Issues a GET request to the `get-session-key` endpoint for
        subsequent use in requests from the `secrets` endpoint.

        :Returns: String containing session key.
        """
        req = requests.post(
            '{}/secrets/get-session-key/?preserve_key=True'.format(self.base),
            headers={
                'accept': 'application/json',
                'authorization': 'Token {}'.format(self.token),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data=urlencode({
                'private_key': self.private_key.strip('\n')
            })
        )
        if req.ok:
            return json.loads(req.text)['session_key']
        else:
            raise RequestError(req)

    @property
    def url(self):
        """ Builds a URL.
        Creates a valid netbox url based on kwargs passed during
        instantiation.

        :Returns: String of URL.
        """
        def construct_url(input):
            for k, v in input.items():
                if isinstance(v, list):
                    for i in v:
                        yield "{}={}".format(k, i)
                else:
                    yield "{}={}".format(k, v)

        if self.key:
            return '{}/{key}/'.format(
                self.base,
                key=self.key
            )
        if self.filters:
            if self.base[-1] == '/':
                return '{}?{query}'.format(
                    self.base,
                    query="&".join(list(construct_url(self.filters)))
                )
            elif '/?' in self.base:
                return '{}&{query}'.format(
                    self.base,
                    query="&".join(list(construct_url(self.filters)))
                )
            else:
                return '{}/?{query}'.format(
                    self.base,
                    query="&".join(list(construct_url(self.filters)))
                )
        else:
            return self.base

    def normalize_url(self, url):
        """ Builds a url for POST actions.
        """
        if url[-1] != '/':
            return "{}/".format(url)

        return url

    def get(self):
        """Makes a GET request.

        Makes a GET request to NetBox's API, and automatically recurses
        any paginated results.

        :raises: RequestError if req.ok returns false.

        :Returns: List of `Response` objects returned from the
            endpoint.
        """
        headers = {
            'accept': 'application/json; version={};'.format(
                self.version or self.get_version()
            )
        }
        if self.token:
            headers.update(authorization='Token {}'.format(self.token))
        if self.session_key:
            headers.update(
                {'X-Session-Key': self.session_key}
            )

        def make_request(url):

            req = requests.get(url, headers=headers)
            if req.ok:
                return json.loads(req.text)
            else:
                raise RequestError(req)

        def req_all(url):
            req = make_request(url)
            if isinstance(req, dict) and req.get('results') is not None:
                ret = req['results']
                first_run = True
                while req['next']:
                    next_url = "{}{}limit={}&offset={}".format(
                        self.url,
                        '&' if self.url[-1] != '/' else '?',
                        req['count'],
                        len(req['results'])
                    ) if first_run else req['next']
                    req = make_request(next_url)
                    first_run = False
                    ret.extend(req['results'])
                return ret
            else:
                return req

        return req_all(self.url)

    def put(self, data):
        """Makes PUT request.

        Makes a PUT request to NetBox's API. Adds the session key to
        headers if the `private_key` attribute was populated.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :returns: Dict containing the response from NetBox's API.
        """
        headers = {
            'Content-Type': 'application/json; version={};'.format(
                self.version or self.get_version()
            ),
            'authorization': 'Token {}'.format(self.token),
        }
        if self.session_key:
            headers.update(
                {'X-Session-Key': self.session_key}
            )
        req = requests.put(self.url, headers=headers, data=json.dumps(data))
        if req.ok:
            return json.loads(req.text)
        else:
            raise RequestError(req)

    def post(self, data):
        """Makes POST request.

        Makes a POST request to NetBox's API. Adds the session key to
        headers if the `private_key` attribute was populated.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :Returns: Dict containing the response from NetBox's API.
        """
        headers = {
            'Content-Type': 'application/json; version={};'.format(
                self.version or self.get_version()
            ),
            'authorization': 'Token {}'.format(self.token),
        }
        if self.session_key:
            headers.update(
                {'X-Session-Key': self.session_key}
            )
        req = requests.post(
            self.normalize_url(self.url),
            headers=headers,
            data=json.dumps(data)
        )
        if req.ok:
            return json.loads(req.text)
        else:
            raise RequestError(req)

    def delete(self):
        """Makes DELETE request.

        Makes a DELETE request to NetBox's API. Adds the session key to
        headers if the `private_key` attribute was populated.

        Returns:
            True if successful.

        Raises:
            RequestError if req.ok doesn't return True.
        """
        headers = {
            'accept': 'application/json; version={};'.format(
                self.version or self.get_version()
            ),
            'authorization': 'Token {}'.format(self.token),
        }
        req = requests.delete(
            "{}".format(self.url),
            headers=headers,
        )
        if req.ok:
            return True
        else:
            raise RequestError(req)
