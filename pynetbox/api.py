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
from pynetbox.lib import Endpoint, Request
from pynetbox import dcim, ipam


class App(object):
    """ Represents apps in NetBox.

    Calls to attributes are returned as Endpoint objects.

    :returns: :py:class:`.Endpoint` matching requested attribute.
    :raises: :py:class:`.RequestError`
        if requested endpoint doesn't exist.
    """
    def __init__(self, app, api_kwargs=None):
        self.app = app
        self.api_kwargs = api_kwargs

    def __getattr__(self, name):
        return Endpoint(
            name,
            api_kwargs=self.api_kwargs,
            app=self.app
        )


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

    :param str url: The base url to the instance of Netbox you
        wish to connect to.
    :param str token: Your netbox token.
    :param str,optional private_key_file: The path to your private
        key file.
    :param str,optional private_key: Your private key.
    :param str,optional version: Override the API version, otherwise
        it's dynamically discovered.
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

    """

    def __init__(self, url, token=None, private_key=None,
                 private_key_file=None, version=None):
        if private_key and private_key_file:
            raise ValueError(
                '"private_key" and "private_key_file" cannot be used together.'
            )
        base_url = "{}/api".format(url)

        self.api_kwargs = {
            "token": token,
            "private_key": private_key,
            "private_key_file": private_key_file,
            "base_url": base_url,
        }

        if self.api_kwargs.get('private_key_file'):
            with open(self.api_kwargs.get('private_key_file'), 'r') as kf:
                private_key = kf.read()
                self.api_kwargs.update(private_key=private_key)
        if not version:
            version = Request(base=base_url).get_version()
        self.api_kwargs.update(version=version)

        req = Request(
            base=base_url,
            token=token,
            private_key=private_key
        )
        if token and private_key:
            self.api_kwargs.update(session_key=req.get_session_key())

        self.dcim = App(dcim, api_kwargs=self.api_kwargs)
        self.ipam = App(ipam, api_kwargs=self.api_kwargs)
        self.circuits = App('circuits', api_kwargs=self.api_kwargs)
        self.secrets = App('secrets', api_kwargs=self.api_kwargs)
        self.tenancy = App('tenancy', api_kwargs=self.api_kwargs)
        self.extras = App('extras', api_kwargs=self.api_kwargs)
        self.virtualization = App('virtualization', api_kwargs=self.api_kwargs)
