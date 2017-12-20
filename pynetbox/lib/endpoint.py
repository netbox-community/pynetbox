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
from collections import defaultdict

from pynetbox.lib.query import Request
from pynetbox.lib.response import Record, IPRecord

CACHE = defaultdict(list)


class Endpoint(object):
    """Represent actions available on endpoints in the Netbox API.

    Takes ``name`` and ``app`` passed from App() and builds the correct
    url to make queries to and the proper Response object to return
    results in.

    :arg str name: Name of endpoint passed to App().
    :arg obj app: Application object containing any endpoint-specific
        classes.
    :arg dict api_kwargs: Vars passed from Api() that contain
        variables that are set when Api is instantiated.

    .. note::

        In order to call NetBox endpoints with dashes in their
        names you should convert the dash to an underscore.
        (E.g. querying the ip-addresses endpoint is done with
        ``nb.ipam.ip_addresses.all()``.)

    """

    def __init__(self, name, app, api_kwargs={}):
        self.app = app
        app_module = app
        if isinstance(app, str):
            app_name = app_module
        else:
            app_name = app_module.__name__.split('.')[-1]
        self.return_obj = self._lookup_ret_obj(name, app_module, app_name)
        self.api_kwargs = api_kwargs
        self.base_url = api_kwargs.get('base_url')
        self.token = api_kwargs.get('token')
        self.version = api_kwargs.get('version')
        self.session_key = api_kwargs.get('session_key')
        self.url = '{base_url}/{app}/{endpoint}'.format(
            base_url=self.base_url,
            app=app_name,
            endpoint=name.replace('_', '-'),
        )
        self.endpoint_name = name
        self.meta = dict(url=self.url)

    def _lookup_ret_obj(self, name, app_module, app_name):
        """Loads unique Response objects.

        This method loads a unique response object for an endpoint if
        it exists. Otherwise return a generic `Record` object.

        :arg str name: Endpoint name.
        :arg str/obj app_module: The application module that
            contains unique Record objects.
        :arg str app_name: App name.

        :Returns: Record (obj)
        """
        app_return_override = {
            'ipam': IPRecord,
        }
        if app_module:
            obj_name = name.title().replace('_', '')
            ret = getattr(
                app_module,
                obj_name,
                app_return_override.get(app_name, Record)
            )
        else:
            ret = Record
        return ret

    def all(self):
        """Queries the 'ListView' of a given endpoint.

        Returns all objects from an endpoint.

        :Returns: List of instantiated objects.

        :Examples:

        >>> nb.dcim.devices.all()
        [test1-a3-oobsw2, test1-a3-oobsw3, test1-a3-oobsw4]
        >>>
        """
        req = Request(
            base='{}/'.format(self.url),
            token=self.token,
            session_key=self.session_key,
            version=self.version,
        )
        ret_kwargs = dict(
            api_kwargs=self.api_kwargs,
            endpoint_meta=self.meta,
        )
        return [
            self.return_obj(i, **ret_kwargs)
            for i in req.get()
        ]

    def get(self, *args, **kwargs):
        """Queries the DetailsView of a given endpoint.

        :arg int,optional key: id for the item to be
            retrieved.

        :arg str,optional \**kwargs: Accepts the same keyword args as
            filter(). Any search argeter the endpoint accepts can
            be added as a keyword arg.

        :returns: A single instantiated objects.

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
            if len(filter_lookup) == 1:
                return filter_lookup[0]
            if len(filter_lookup) == 0:
                return None
            else:
                raise ValueError('get() returned more than one result.')

        req = Request(
            key=key,
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            version=self.version
        )
        ret_kwargs = dict(
            api_kwargs=self.api_kwargs,
            endpoint_meta=self.meta,
        )

        return self.return_obj(req.get(), **ret_kwargs)

    def filter(self, *args, **kwargs):
        """Queries the 'ListView' of a given endpoint.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argeter if the endpoint supports it.

        :arg str,optional \*args: Freeform search string that's
            accepted on given endpoint.
        :arg str,optional \**kwargs: Any search argeter the
            endpoint accepts can be added as a keyword arg.
            *(Note: Cache is a reserved kwarg.)*

        :Returns: A list of instantiated objects.

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

        cache = kwargs.pop('cache', False)

        if len(args) > 0:
            kwargs.update({'q': args[0]})

        if cache:
            ret = CACHE.get(self.endpoint_name)
            if ret:
                return ret

        req = Request(
            filters=kwargs,
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            version=self.version,
        )
        ret_kwargs = dict(
            api_kwargs=self.api_kwargs,
            endpoint_meta=self.meta,
        )
        ret = [
            self.return_obj(i, **ret_kwargs)
            for i in req.get()
        ]
        CACHE[self.endpoint_name].extend(ret)
        return ret

    def create(self, *args, **kwargs):
        """Creates an object on an endpoint.

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

        :returns: A response from NetBox as a dictionary or list of
            dictionaries.

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

        return Request(
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            version=self.version,
        ).post(args[0] if len(args) > 0 else kwargs)


class DetailEndpoint(object):
    '''Enables read/write Operations on detail endpoints.

    Endpoints like ``available-ips`` that are detail routes off
    traditional endpoints are handled with this class.
    '''

    def __init__(self, name, parent_obj=None):
        self.token = parent_obj.api_kwargs.get('token')
        self.version = parent_obj.api_kwargs.get('version')
        self.session_key = parent_obj.api_kwargs.get('session_key')
        self.url = "{}/{}/{}/".format(
            parent_obj.endpoint_meta.get('url'),
            parent_obj.id,
            name
        )
        self.request_kwargs = dict(
            base=self.url,
            token=self.token,
            session_key=self.session_key,
            version=self.version,
        )

    def list(self):
        """The view operation for a detail endpoint

        Returns the response from NetBox for a detail endpoint.

        :returns: A dictionary or list of dictionaries its retrieved
            from NetBox.
        """
        return Request(**self.request_kwargs).get()

    def create(self, data={}):
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
