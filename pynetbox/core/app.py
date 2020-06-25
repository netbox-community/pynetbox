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
from pynetbox.models import dcim, ipam, virtualization, circuits, extras


class App(object):
    """ Represents apps in NetBox.

    Calls to attributes are returned as Endpoint objects.

    :returns: :py:class:`.Endpoint` matching requested attribute.
    :raises: :py:class:`.RequestError`
        if requested endpoint doesn't exist.
    """

    def __init__(self, api, name):
        self.api = api
        self.name = name
        self._choices = None
        self._setmodel()

    models = {
        "dcim": dcim,
        "ipam": ipam,
        "circuits": circuits,
        "virtualization": virtualization,
        "extras": extras,
    }

    def _setmodel(self):
        self.model = App.models[self.name] if self.name in App.models else None

    def __getstate__(self):
        return {"api": self.api, "name": self.name, "_choices": self._choices}

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._setmodel()

    def __getattr__(self, name):
        if name == "secrets":
            self._set_session_key()
        return Endpoint(self.api, self, name, model=self.model)

    def _set_session_key(self):
        if getattr(self.api, "session_key"):
            return
        if self.api.token and self.api.private_key:
            self.api.session_key = Request(
                base=self.api.base_url,
                token=self.api.token,
                private_key=self.api.private_key,
                http_session=self.api.http_session,
            ).get_session_key()

    def choices(self):
        """ Returns _choices response from App

        .. note::

            This method is deprecated and only works with NetBox version 2.7.x
            or older. The ``choices()`` method in :py:class:`.Endpoint` is
            compatible with all NetBox versions.

        :Returns: Raw response from NetBox's _choices endpoint.
        """
        if self._choices:
            return self._choices

        self._choices = Request(
            base="{}/{}/_choices/".format(self.api.base_url, self.name),
            token=self.api.token,
            private_key=self.api.private_key,
            http_session=self.api.http_session,
        ).get()

        return self._choices

    def custom_choices(self):
        """ Returns _custom_field_choices response from app

        :Returns: Raw response from NetBox's _custom_field_choices endpoint.
        :Raises: :py:class:`.RequestError` if called for an invalid endpoint.
        :Example:

        >>> nb.extras.custom_choices()
        {'Testfield1': {'Testvalue2': 2, 'Testvalue1': 1},
         'Testfield2': {'Othervalue2': 4, 'Othervalue1': 3}}
        """
        custom_field_choices = Request(
            base="{}/{}/_custom_field_choices/".format(self.api.base_url, self.name,),
            token=self.api.token,
            private_key=self.api.private_key,
            http_session=self.api.http_session,
        ).get()
        return custom_field_choices
