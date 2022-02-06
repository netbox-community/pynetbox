"""
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
"""
import sys

import requests

from pynetbox.core.query import Request
from pynetbox.core.app import App, PluginsApp
from pynetbox.core.response import Record


class Api(object):
    """The API object is the point of entry to pynetbox.

    After instantiating the Api() with the appropriate named arguments
    you can specify which app and endpoint you wish to interact with.

    Valid attributes currently are:
        * dcim
        * ipam
        * circuits
        * secrets (on NetBox 2.11 and older)
        * tenancy
        * extras
        * virtualization
        * users (since NetBox 2.9)
        * wireless (since NetBox 3.1)

    Calling any of these attributes will return
    :py:class:`.App` which exposes endpoints as attributes.

    **Additional Attributes**:
        *  **http_session(requests.Session)**:
                Override the default session with your own. This is used to control
                a number of HTTP behaviors such as SSL verification, custom headers,
                retires, and timeouts.
                See `custom sessions <advanced.html#custom-sessions>`__ for more info.

    :param str url: The base URL to the instance of NetBox you
        wish to connect to.
    :param str token: Your NetBox token.
    :param str,optional private_key_file: The path to your private
        key file. (Usable only on NetBox 2.11 and older)
    :param str,optional private_key: Your private key. (Usable only on NetBox 2.11 and older)
    :param bool,optional threading: Set to True to use threading in ``.all()``
        and ``.filter()`` requests.
    :raises ValueError: If *private_key* and *private_key_file* are both
        specified.
    :raises AttributeError: If app doesn't exist.
    :Examples:

    >>> import pynetbox
    >>> nb = pynetbox.api(
    ...     'http://localhost:8000',
    ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
    ... )
    >>> list(nb.dcim.devices.all())
    [test1-leaf1, test1-leaf2, test1-leaf3]
    """

    def __init__(
        self,
        url,
        token=None,
        private_key=None,
        private_key_file=None,
        threading=False,
    ):
        if private_key and private_key_file:
            raise ValueError(
                '"private_key" and "private_key_file" cannot be used together.'
            )
        base_url = "{}/api".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.private_key = private_key
        self.private_key_file = private_key_file
        self.base_url = base_url
        self.session_key = None
        self.http_session = requests.Session()
        if threading and sys.version_info.major == 2:
            raise NotImplementedError(
                "Threaded pynetbox calls not supported                 in Python 2"
            )
        self.threading = threading

        if self.private_key_file:
            with open(self.private_key_file, "r") as kf:
                private_key = kf.read()
                self.private_key = private_key

        self.dcim = App(self, "dcim")
        self.ipam = App(self, "ipam")
        self.circuits = App(self, "circuits")
        self.secrets = App(self, "secrets")
        self.tenancy = App(self, "tenancy")
        self.extras = App(self, "extras")
        self.virtualization = App(self, "virtualization")
        self.users = App(self, "users")
        self.wireless = App(self, "wireless")
        self.plugins = PluginsApp(self)

    @property
    def version(self):
        """Gets the API version of NetBox.

        Can be used to check the NetBox API version if there are
        version-dependent features or syntaxes in the API.

        :Returns: Version number as a string.
        :Example:

        >>> import pynetbox
        >>> nb = pynetbox.api(
        ...     'http://localhost:8000',
        ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
        ... )
        >>> nb.version
        '3.1'
        >>>
        """
        version = Request(
            base=self.base_url,
            http_session=self.http_session,
        ).get_version()
        return version

    def openapi(self):
        """Returns the OpenAPI spec.

        Quick helper function to pull down the entire OpenAPI spec.

        :Returns: dict
        :Example:

        >>> import pynetbox
        >>> nb = pynetbox.api(
        ...     'http://localhost:8000',
        ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
        ... )
        >>> nb.openapi()
        {...}
        >>>
        """
        return Request(
            base=self.base_url,
            http_session=self.http_session,
        ).get_openapi()

    def status(self):
        """Gets the status information from NetBox.

        Available in NetBox 2.10.0 or newer.

        :Returns: Dictionary as returned by NetBox.
        :Raises: :py:class:`.RequestError` if the request is not successful.
        :Example:

        >>> pprint.pprint(nb.status())
        {'django-version': '3.1.3',
         'installed-apps': {'cacheops': '5.0.1',
                            'debug_toolbar': '3.1.1',
                            'django_filters': '2.4.0',
                            'django_prometheus': '2.1.0',
                            'django_rq': '2.4.0',
                            'django_tables2': '2.3.3',
                            'drf_yasg': '1.20.0',
                            'mptt': '0.11.0',
                            'rest_framework': '3.12.2',
                            'taggit': '1.3.0',
                            'timezone_field': '4.0'},
         'netbox-version': '2.10.2',
         'plugins': {},
         'python-version': '3.7.3',
         'rq-workers-running': 1}
        >>>
        """
        status = Request(
            base=self.base_url,
            token=self.token,
            http_session=self.http_session,
        ).get_status()
        return status

    def create_token(self, username, password):
        """Creates an API token using a valid NetBox username and password.
        Saves the created token automatically in the API object.

        Requires NetBox 3.0.0 or newer.

        :Returns: The token as a ``Record`` object.
        :Raises: :py:class:`.RequestError` if the request is not successful.

        :Example:

        >>> import pynetbox
        >>> nb = pynetbox.api("https://netbox-server")
        >>> token = nb.create_token("admin", "netboxpassword")
        >>> nb.token
        '96d02e13e3f1fdcd8b4c089094c0191dcb045bef'
        >>> from pprint import pprint
        >>> pprint(dict(token))
        {'created': '2021-11-27T11:26:49.360185+02:00',
         'description': '',
         'display': '045bef (admin)',
         'expires': None,
         'id': 2,
         'key': '96d02e13e3f1fdcd8b4c089094c0191dcb045bef',
         'url': 'https://netbox-server/api/users/tokens/2/',
         'user': {'display': 'admin',
                  'id': 1,
                  'url': 'https://netbox-server/api/users/users/1/',
                  'username': 'admin'},
         'write_enabled': True}
        >>>
        """
        resp = Request(
            base="{}/users/tokens/provision/".format(self.base_url),
            http_session=self.http_session,
        ).post(data={"username": username, "password": password})
        # Save the newly created API token, otherwise populating the Record
        # object details will fail
        self.token = resp["key"]
        return Record(resp, self, None)
