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
from pynetbox.core.query import Request, url_param_builder
from pynetbox.core.response import Record

RESERVED_KWARGS = ("id", "pk", "limit", "offset")


class Endpoint(object):
    """Represent actions available on endpoints in the Netbox API.

    Takes ``name`` and ``app`` passed from App() and builds the correct
    url to make queries to and the proper Response object to return
    results in.

    :arg obj api: Takes :py:class:`.Api` created at instantiation.
    :arg obj app: Takes :py:class:`.App`.
    :arg str name: Name of endpoint passed to App().
    :arg obj,optional model: Custom model for given app.

    .. note::

        In order to call NetBox endpoints with dashes in their
        names you should convert the dash to an underscore.
        (E.g. querying the ip-addresses endpoint is done with
        ``nb.ipam.ip_addresses.all()``.)

    """

    def __init__(self, api, app, name, model=None):
        self.return_obj = self._lookup_ret_obj(name, model)
        self.api = api
        self.base_url = api.base_url
        self.token = api.token
        self.session_key = api.session_key
        self.ssl_verify = api.ssl_verify
        self.url = "{base_url}/{app}/{endpoint}".format(
            base_url=self.base_url,
            app=app.name,
            endpoint=name.replace("_", "-"),
        )

    def _lookup_ret_obj(self, name, model):
        """Loads unique Response objects.

        This method loads a unique response object for an endpoint if
        it exists. Otherwise return a generic `Record` object.

        :arg str name: Endpoint name.
        :arg obj model: The application model that
            contains unique Record objects.

        :Returns: Record (obj)
        """
        if model:
            name = name.title().replace("_", "")
            ret = getattr(model, name, Record)
        else:
            ret = Record
        return ret

    def _response_loader(self, values):
        return self.return_obj(values, self.api, self)

    def all(self):
        """Queries the 'ListView' of a given endpoint.

        Returns all objects from an endpoint.

        :Returns: List of :py:class:`.Record` objects.

        :Examples:

        >>> nb.dcim.devices.all()
        [test1-a3-oobsw2, test1-a3-oobsw3, test1-a3-oobsw4]
        >>>
        """
        req = Request(
            base="{}/".format(self.url),
            token=self.token,
            session_key=self.session_key,
            ssl_verify=self.ssl_verify,
        )

        return [self._response_loader(i) for i in req.get()]

    def get(self, *args, **kwargs):
        r"""Queries the DetailsView of a given endpoint.

        :arg int,optional key: id for the item to be
            retrieved.

        :arg str,optional \**kwargs: Accepts the same keyword args as
            filter(). Any search argument the endpoint accepts can
            be added as a keyword arg.

        :returns: A single :py:class:`.Record` object.

        :raises ValueError: if kwarg search return more than one value.

        :Examples:

        Referencing with a kwarg that only returns one value.

        >>> nb.dcim.devices.get(name='test1-a3-tor1b')
        test1-a3-tor1b
        >>>

        Referencing with an id.

        >>> nb.dcim.devices.get(1)
        test1-edge1
        >>>
        """

        try:
            key = args[0]
        except IndexError:
            key = None

        if not key:
            filter_lookup = self.filter(**kwargs)
            if filter_lookup:
                if len(filter_lookup) > 1:
                    raise ValueError(
                        "get() returned more than one result. "
                        "Check that the kwarg(s) passed are valid for this "
                        "endpoint or use filter() or all() instead."
                    )
                else:
                    return filter_lookup[0]
            return filter_lookup

        req = Request(
            key=key,
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            ssl_verify=self.ssl_verify,
        )

        return self._response_loader(req.get())

    def filter(self, *args, **kwargs):
        r"""Queries the 'ListView' of a given endpoint.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it.

        :arg str,optional \*args: Freeform search string that's
            accepted on given endpoint.
        :arg str,optional \**kwargs: Any search argument the
            endpoint accepts can be added as a keyword arg.

        :Returns: A list of :py:class:`.Record` objects.

        :Examples:

        To return a list of objects matching a named argument filter.

        >>> nb.dcim.devices.filter(role='leaf-switch')
        [test1-a3-tor1b, test1-a3-tor1c, test1-a3-tor1d, test1-a3-tor2a]
        >>>

        Using a freeform query along with a named argument.

        >>> nb.dcim.devices.filter('a3', role='leaf-switch')
        [test1-a3-tor1b, test1-a3-tor1c, test1-a3-tor1d, test1-a3-tor2a]
        >>>

        Chaining multiple named arguments.

        >>> nb.dcim.devices.filter(role='leaf-switch', status=True)
        [test1-leaf2]
        >>>

        Passing a list as a named argument adds multiple filters of the
        same value.

        >>> nb.dcim.devices.filter(role=['leaf-switch', 'spine-switch'])
        [test1-a3-spine1, test1-a3-spine2, test1-a3-leaf1]
        >>>
        """

        if args:
            kwargs.update({"q": args[0]})

        if not kwargs:
            raise ValueError(
                "filter must be passed kwargs. Perhaps use all() instead."
            )
        if any(i in RESERVED_KWARGS for i in kwargs):
            raise ValueError(
                "A reserved {} kwarg was passed. Please remove it "
                "try again.".format(RESERVED_KWARGS)
            )

        req = Request(
            filters=kwargs,
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            ssl_verify=self.ssl_verify,
        )

        ret = [self._response_loader(i) for i in req.get()]
        return ret

    def create(self, *args, **kwargs):
        r"""Creates an object on an endpoint.

        Allows for the creation of new objects on an endpoint. Named
        arguments are converted to json properties, and a single object
        is created. NetBox's bulk creation capabilities can be used by
        passing a list of dictionaries as the first argument.

        .. note:

            Any positional arguments will supercede named ones.

        :arg list \*args: A list of dictionaries containing the
            properties of the objects to be created.
        :arg str \**kwargs: key/value strings representing
            properties on a json object.

        :returns: A list or single :py:class:`.Record` object depending
            on whether a bulk creation was requested.

        :Examples:

        Creating an object on the `devices` endpoint you can lookup a
        device_role's name with:

        >>> netbox.dcim.devices.create(
        ...    name='test',
        ...    device_role=1,
        ... )
        >>>

        Use bulk creation by passing a list of dictionaries:

        >>> nb.dcim.devices.create([
        ...     {
        ...         "name": "test1-core3",
        ...         "device_role": 3,
        ...         "site": 1,
        ...         "device_type": 1,
        ...         "status": 1
        ...     },
        ...     {
        ...         "name": "test1-core4",
        ...         "device_role": 3,
        ...         "site": 1,
        ...         "device_type": 1,
        ...         "status": 1
        ...     }
        ... ])
        """

        req = Request(
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            ssl_verify=self.ssl_verify,
        ).post(args[0] if args else kwargs)

        if isinstance(req, list):
            return [self._response_loader(i) for i in req]

        return self._response_loader(req)


class DetailEndpoint(object):
    """Enables read/write Operations on detail endpoints.

    Endpoints like ``available-ips`` that are detail routes off
    traditional endpoints are handled with this class.
    """

    def __init__(self, parent_obj, name, custom_return=None):
        self.parent_obj = parent_obj
        self.custom_return = custom_return
        self.url = "{}/{}/{}/".format(
            parent_obj.endpoint.url, parent_obj.id, name
        )
        self.request_kwargs = dict(
            base=self.url,
            token=parent_obj.api.token,
            session_key=parent_obj.api.session_key,
            ssl_verify=parent_obj.api.ssl_verify,
        )

    def list(self, **kwargs):
        r"""The view operation for a detail endpoint

        Returns the response from NetBox for a detail endpoint.

        :args \**kwargs: key/value pairs that get converted into url
            parameters when passed to the endpoint.
            E.g. ``.list(method='get_facts')`` would be converted to
            ``.../?method=get_facts``.

        :returns: A dictionary or list of dictionaries retrieved from
            NetBox.
        """
        if kwargs:
            self.request_kwargs["base"] = "{}{}".format(
                self.url, url_param_builder(kwargs)
            )
        req = Request(**self.request_kwargs).get()

        if self.custom_return:
            if isinstance(req, list):
                return [
                    self.custom_return(
                        i, self.parent_obj.api, self.parent_obj.endpoint
                    )
                    for i in req
                ]
            return self.custom_return(
                req, self.parent_obj.api, self.parent_obj.endpoint
            )
        return req

    def create(self, data):
        """The write operation for a detail endpoint.

        Creates objects on a detail endpoint in NetBox.

        :arg dict/list,optional data: A dictionary containing the
            key/value pair of the items you're creating on the parent
            object. Defaults to empty dict which will create a single
            item with default values.

        :returns: A dictionary or list of dictionaries its created in
            NetBox.
        """
        return Request(**self.request_kwargs).post(data)


class RODetailEndpoint(DetailEndpoint):
    def create(self, data):
        raise NotImplementedError(
            "Writes are not supported for this endpoint."
        )
