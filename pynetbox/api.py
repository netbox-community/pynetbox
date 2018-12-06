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
from pynetbox.core.endpoint import Endpoint
from pynetbox.core.query import Request
from pynetbox.models import dcim, ipam, virtualization, circuits


class App(object):
    """ Represents apps in NetBox.

    Calls to attributes are returned as Endpoint objects.

    :returns: :py:class:`.Endpoint` matching requested attribute.
    :raises: :py:class:`.RequestError`
        if requested endpoint doesn't exist.
    """

    def __init__(self, api, name, model=None):
        self.api = api
        self.name = name
        self.model = model
        self._choices = None

    def __getattr__(self, name):
        return Endpoint(self.api, self, name, model=self.model)

    def choices(self):
        """ Returns _choices response from App

        :Returns: Raw response from NetBox's _choices endpoint.
        """
        if self._choices:
            return self._choices

        self._choices = Request(
            base="{}/{}/_choices/".format(self.api.base_url, self.name),
            token=self.api.token,
            private_key=self.api.private_key,
            ssl_verify=self.api.ssl_verify,
        ).get()

        return self._choices


class Api(object):
    """ The API object is the point of entry to pynetbox.

    After instantiating the Api() with the appropriate named arguments
    you can specify which app and endpoint you wish to interact with.

    Valid attributes currently are:
        * dcim
        * ipam
        * circuits
        * secrets
        * tenancy
        * extras
        * virtualization

    Calling any of these attributes will return
    :py:class:`.App` which exposes endpoints as attributes.

    :type ssl_verify: bool or str
    :param str url: The base url to the instance of Netbox you
        wish to connect to.
    :param str token: Your netbox token.
    :param str,optional private_key_file: The path to your private
        key file.
    :param str,optional private_key: Your private key.
    :param bool/str,optional ssl_verify: Specify SSL verification behavior
        see: requests_.
    :raises ValueError: If *private_key* and *private_key_file* are both
        specified.
    :raises AttributeError: If app doesn't exist.
    :Examples:

    >>> import pynetbox
    >>> nb = pynetbox.api(
    ...     'http://localhost:8000',
    ...     private_key_file='/path/to/private-key.pem',
    ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
    ... )
    >>> nb.dcim.devices.all()

    .. _requests: http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
    """  # noqa

    def __init__(
        self,
        url,
        token=None,
        private_key=None,
        private_key_file=None,
        ssl_verify=True,
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
        self.ssl_verify = ssl_verify
        self.session_key = None

        if self.private_key_file:
            with open(self.private_key_file, "r") as kf:
                private_key = kf.read()
                self.private_key = private_key

        req = Request(
            base=base_url,
            token=token,
            private_key=private_key,
            ssl_verify=ssl_verify,
        )
        if self.token and self.private_key:
            self.session_key = req.get_session_key()

        self.dcim = App(self, "dcim", model=dcim)
        self.ipam = App(self, "ipam", model=ipam)
        self.circuits = App(self, "circuits", model=circuits)
        self.secrets = App(self, "secrets", model=None)
        self.tenancy = App(self, "tenancy", model=None)
        self.extras = App(self, "extras", model=None)
        self.virtualization = App(self, "virtualization", model=virtualization)
