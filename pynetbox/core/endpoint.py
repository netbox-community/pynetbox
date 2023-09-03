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
from pynetbox.core.query import Request, RequestError
from pynetbox.core.response import Record, RecordSet

RESERVED_KWARGS = ()


class Endpoint:
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
        self.name = name.replace("_", "-")
        self.api = api
        self.base_url = api.base_url
        self.token = api.token
        self.url = "{base_url}/{app}/{endpoint}".format(
            base_url=self.base_url,
            app=app.name,
            endpoint=self.name,
        )
        self._choices = None

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

    def all(self, limit=0, offset=None):
        """Queries the 'ListView' of a given endpoint.

        Returns all objects from an endpoint.

        :arg int,optional limit: Overrides the max page size on
            paginated returns.  This defines the number of records that will
            be returned with each query to the Netbox server.  The queries
            will be made as you iterate through the result set.
        :arg int,optional offset: Overrides the offset on paginated returns.

        :Returns: A :py:class:`.RecordSet` object.

        :Examples:

        >>> devices = list(nb.dcim.devices.all())
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-leaf1
        test1-leaf2
        test1-leaf3
        >>>

        If you want to iterate over the results multiple times then
        encapsulate them in a list like this:
        >>> devices = list(nb.dcim.devices.all())

        This will cause the entire result set
        to be fetched from the server.

        """
        if limit == 0 and offset is not None:
            raise ValueError("offset requires a positive limit value")
        req = Request(
            base="{}/".format(self.url),
            token=self.token,
            http_session=self.api.http_session,
            threading=self.api.threading,
            limit=limit,
            offset=offset,
        )

        return RecordSet(self, req)

    def get(self, *args, **kwargs):
        r"""Queries the DetailsView of a given endpoint.

        :arg int,optional key: id for the item to be
            retrieved.

        :arg str,optional \**kwargs: Accepts the same keyword args as
            filter(). Any search argument the endpoint accepts can
            be added as a keyword arg.

        :returns: A single :py:class:`.Record` object or None

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

        Using multiple named arguments. For example, retriving the location when the location name is not unique and used in multiple sites.

        >>> nb.locations.get(site='site-1', name='Row 1')
        Row 1
        """

        try:
            key = args[0]
        except IndexError:
            key = None

        if not key:
            resp = self.filter(**kwargs)
            ret = next(resp, None)
            if not ret:
                return ret
            try:
                next(resp)
                raise ValueError(
                    "get() returned more than one result. "
                    "Check that the kwarg(s) passed are valid for this "
                    "endpoint or use filter() or all() instead."
                )
            except StopIteration:
                return ret

        req = Request(
            key=key,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )
        try:
            return next(RecordSet(self, req), None)
        except RequestError as e:
            if e.req.status_code == 404:
                return None
            else:
                raise e

    def filter(self, *args, **kwargs):
        r"""Queries the 'ListView' of a given endpoint.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it.

        :arg str,optional \*args: Freeform search string that's
            accepted on given endpoint.
        :arg str,optional \**kwargs: Any search argument the
            endpoint accepts can be added as a keyword arg.
        :arg int,optional limit: Overrides the max page size on
            paginated returns.  This defines the number of records that will
            be returned with each query to the Netbox server.  The queries
            will be made as you iterate through the result set.
        :arg int,optional offset: Overrides the offset on paginated returns.

        :Returns: A :py:class:`.RecordSet` object.

        :Examples:

        To return a list of objects matching a named argument filter.

        >>> devices = nb.dcim.devices.filter(role='leaf-switch')
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-leaf1
        test1-leaf2
        test1-leaf3
        >>>

        >>> devices = nb.dcim.devices.filter(site='site-1')
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-a2-leaf1
        test2-a2-leaf2
        >>>

        If we want to filter by site, location, tenant, or fields which have a display name and a slug, the slug has to be used for filtering.

        .. note::

          If a keyword argument is incorrect a `TypeError` will not be returned by pynetbox.
          Instead, all records filtered up to the last correct keyword argument. For example, if we used `site="Site 1"` instead of `site=site-1` when using filter on
          the devices endpoint, then pynetbox will return **all** devices across all sites instead of devices at Site 1.


        Using a freeform query along with a named argument.

        >>> devices = nb.dcim.devices.filter('a3', role='leaf-switch')
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-a3-leaf1
        test1-a3-leaf2
        >>>


        Chaining multiple named arguments.

        >>> devices = nb.dcim.devices.filter(role='leaf-switch', status=True)
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-leaf2
        >>>

        Passing a list as a named argument adds multiple filters of the
        same value.

        >>> devices = nb.dcim.devices.filter(role=['leaf-switch', 'spine-switch'])
        >>> for device in devices:
        ...     print(device.name)
        ...
        test1-a3-spine1
        test1-a3-spine2
        test1-a3-leaf1
        >>>

        To have the ability to iterate over the results multiple times then
        encapsulate them in a list.  This will cause the entire result set
        to be fetched from the server.

        >>> devices = list(nb.dcim.devices.filter(role='leaf-switch'))
        """

        if args:
            kwargs.update({"q": args[0]})

        if any(i in RESERVED_KWARGS for i in kwargs):
            raise ValueError(
                "A reserved kwarg was passed ({}). Please remove it "
                "and try again.".format(RESERVED_KWARGS)
            )
        limit = kwargs.pop("limit") if "limit" in kwargs else 0
        offset = kwargs.pop("offset") if "offset" in kwargs else None
        if limit == 0 and offset is not None:
            raise ValueError("offset requires a positive limit value")
        req = Request(
            filters=kwargs,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
            threading=self.api.threading,
            limit=limit,
            offset=offset,
        )

        return RecordSet(self, req)

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

        Creating an object on the `devices` endpoint:

        >>> device = netbox.dcim.devices.create(
        ...    name='test',
        ...    role=1,
        ... )
        >>>

        Creating an object on the 'devices' endpoint using `.get()` to get ids.

        >>> device = netbox.dcim.devices.create(
        ...     name = 'test1',
        ...     site = netbox.dcim.devices.get(name='site1').id,
        ...     location = netbox.dcim.locations.get(name='Row 1').id,
        ...     rack = netbox.dcim.racks.get(facility_id=1).id,
        ...     device_type = netbox.dcim.device_types.get(slug='server-type-1').id,
        ...     status='active',
        ...     )
        >>>

        Use bulk creation by passing a list of dictionaries:

        >>> nb.dcim.devices.create([
        ...     {
        ...         "name": "test1-core3",
        ...         "role": 3,
        ...         "site": 1,
        ...         "device_type": 1,
        ...         "status": 1
        ...     },
        ...     {
        ...         "name": "test1-core4",
        ...         "role": 3,
        ...         "site": 1,
        ...         "device_type": 1,
        ...         "status": 1
        ...     }
        ... ])

        Create a new device type.

        >>> device_type = netbox.dcim.devices.create(
        ...     manufacturer = netbox.dcim.manufacturers.get(name='manufacturer-name').id,
        ...     model = 'device-type-name',
        ...     slug = 'device-type-slug',
        ...     subdevice_role = 'child or parent', #optional field - requred if creating a device type to be used by child devices
        ...     u_height = unit_height, #can only equal 0 if the device type is for a child device - requires subdevice_role='child' if that is the case
        ...     custom_fields = {'cf_1' : 'custom data 1'}
        ...     )

        Create a device bay and child device.

        >>> device_bay = netbox.dcim.device_bays.create(
        ...     device = netbox.dcim.devices.get(name='parent device').id, # device the device bay is located
        ...     name = 'Bay 1'
        ...     )
        >>> child_device = netbox.dcim.devices.create(
        ...     name = 'child device',
        ...     site = netbox.dcim.devices.get(name='test-site').id,
        ...     location = netbox.dcim.locations.get(name='row-1').id,
        ...     tenant = netbox.tenancy.tenants.get(name='tenant-1').id,
        ...     manufactuer = netbox.dcim.manufacturers.get(name='test-m').id,
        ...     rack = netbox.dcim.racks.get(name='Test Rack').id,
        ...     device_type = netbox.dcim.device.types.get(slug='test-server').id, #easier to get device_type id by search by its slug rather than by its name
        ...     )
        >>> get_device_bay = netbox.dcim.device_bays.get(name='Bay 1')
        >>> get_child_device = netbox.dcim.devices.get(name='child device')
        >>> get_device_bay.installed_device = get_child_device
        >>> get_device_bay.save()

        Create a network interface

        >>> interface = netbox.dcim.interfaces.get(name="interface-test", device="test-device")
        >>> netbox_ip = netbox.ipam.ip_addresses.create(
        ... address = "ip-address",
        ... tenant = netbox.tenancy.tenants.get(name='tenant-1').id,
        ... tags = [{'name':'Tag 1'}],
        ... )
        >>> #assign IP Address to device's network interface
        >>> netbox_ip.assigned_object = interface
        >>> netbox_ip.assigned_object_id = interface.id
        >>> netbox_ip.assigned_object_type = 'dcim.interface'
        >>> # add dns name to IP Address (optional)
        >>> netbox_ip.dns_name = "test.dns.local"
        >>> # save changes to IP Address
        >>> netbox_ip.save()

        """

        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        ).post(args[0] if args else kwargs)

        if isinstance(req, list):
            return [self.return_obj(i, self.api, self) for i in req]
        return self.return_obj(req, self.api, self)

    def update(self, objects):
        r"""Bulk updates existing objects on an endpoint.

        Allows for bulk updating of existing objects on an endpoint.
        Objects is a list whic contain either json/dicts or Record
        derived objects, which contain the updates to apply.
        If json/dicts are used, then the id of the object *must* be
        included

        :arg list objects: A list of dicts or Record.

        :returns: True if the update succeeded

        :Examples:

        Updating objects on the `devices` endpoint:

        >>> devices = nb.dcim.devices.update([
        ...    {'id': 1, 'name': 'test'},
        ...    {'id': 2, 'name': 'test2'},
        ... ])
        >>> devices
        [test2, test]
        >>>

        Use bulk update by passing a list of Records:

        >>> devices = list(nb.dcim.devices.filter())
        >>> devices
        [Device1, Device2, Device3]
        >>> for d in devices:
        ...     d.name = d.name+'-test'
        ...
        >>> nb.dcim.devices.update(devices)
        [Device1-test, Device2-test, Device3-test]
        >>>
        """
        series = []
        if not isinstance(objects, list):
            raise ValueError(
                "Objects passed must be list[dict|Record] - was {}".format(
                    type(objects)
                )
            )
        for o in objects:
            if isinstance(o, Record):
                data = o.updates()
                if data:
                    data["id"] = o.id
                    series.append(data)
            elif isinstance(o, dict):
                if "id" not in o:
                    raise ValueError("id is missing from object: " + str(o))
                series.append(o)
            else:
                raise ValueError(
                    "Object passed must be dict|Record - was {}".format(type(objects))
                )
        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        ).patch(series)

        if isinstance(req, list):
            return [self.return_obj(i, self.api, self) for i in req]
        return self.return_obj(req, self.api, self)

    def delete(self, objects):
        r"""Bulk deletes objects on an endpoint.

        Allows for batch deletion of multiple objects from
        a single endpoint

        :arg list objects: A list of either ids or Records or
            a single RecordSet to delete.
        :returns: True if bulk DELETE operation was successful.

        :Examples:

        Deleting all `devices`:

        >>> netbox.dcim.devices.delete(netbox.dcim.devices.all(0))
        >>>

        Use bulk deletion by passing a list of ids:

        >>> netbox.dcim.devices.delete([2, 243, 431, 700])
        >>>

        Use bulk deletion to delete objects eg. when filtering
        on a `custom_field`:
        >>> netbox.dcim.devices.delete([
        >>>         d for d in netbox.dcim.devices.all(0) \
        >>>             if d.custom_fields.get('field', False)
        >>>     ])
        >>>
        """
        cleaned_ids = []
        if not isinstance(objects, list) and not isinstance(objects, RecordSet):
            raise ValueError(
                "objects must be list[str|int|Record]"
                "|RecordSet - was " + str(type(objects))
            )
        for o in objects:
            if isinstance(o, int):
                cleaned_ids.append(o)
            elif isinstance(o, str) and o.isnumeric():
                cleaned_ids.append(int(o))
            elif isinstance(o, Record):
                if not hasattr(o, "id"):
                    raise ValueError(
                        "Record from '"
                        + o.url
                        + "' does not have an id and cannot be bulk deleted"
                    )
                cleaned_ids.append(o.id)
            else:
                raise ValueError(
                    "Invalid object in list of objects to delete: " + str(type(o))
                )

        req = Request(
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )
        return True if req.delete(data=[{"id": i} for i in cleaned_ids]) else False

    def choices(self):
        """Returns all choices from the endpoint.

        The returned dict is also saved in the endpoint object (in
        ``_choices`` attribute) so that later calls will return the same data
        without recurring requests to NetBox. When using ``.choices()`` in
        long-running applications, consider restarting them whenever NetBox is
        upgraded, to prevent using stale choices data.

        :Returns: Dict containing the available choices.

        :Example:

        >>> from pprint import pprint
        >>> pprint(nb.ipam.ip_addresses.choices())
        {'role': [{'display_name': 'Loopback', 'value': 'loopback'},
                  {'display_name': 'Secondary', 'value': 'secondary'},
                  {'display_name': 'Anycast', 'value': 'anycast'},
                  {'display_name': 'VIP', 'value': 'vip'},
                  {'display_name': 'VRRP', 'value': 'vrrp'},
                  {'display_name': 'HSRP', 'value': 'hsrp'},
                  {'display_name': 'GLBP', 'value': 'glbp'},
                  {'display_name': 'CARP', 'value': 'carp'}],
         'status': [{'display_name': 'Active', 'value': 'active'},
                    {'display_name': 'Reserved', 'value': 'reserved'},
                    {'display_name': 'Deprecated', 'value': 'deprecated'},
                    {'display_name': 'DHCP', 'value': 'dhcp'},
                    {'display_name': 'SLAAC', 'value': 'slaac'}]}
        >>>
        """
        if self._choices:
            return self._choices

        req = Request(
            base=self.url,
            token=self.api.token,
            http_session=self.api.http_session,
        ).options()
        try:
            post_data = req["actions"]["POST"]
        except KeyError:
            raise ValueError(
                "Unexpected format in the OPTIONS response at {}".format(self.url)
            )
        self._choices = {}
        for prop in post_data:
            if "choices" in post_data[prop]:
                self._choices[prop] = post_data[prop]["choices"]

        return self._choices

    def count(self, *args, **kwargs):
        r"""Returns the count of objects in a query.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it. If no
        arguments are passed the count for all objects on an endpoint
        are returned.

        :arg str,optional \*args: Freeform search string that's
            accepted on given endpoint.
        :arg str,optional \**kwargs: Any search argument the
            endpoint accepts can be added as a keyword arg.

        :Returns: Integer with count of objects returns by query.

        :Examples:

        To return a count of objects matching a named argument filter.

        >>> nb.dcim.devices.count(site='tst1')
        5827
        >>>

        To return a count of objects on an entire endpoint.

        >>> nb.dcim.devices.count()
        87382
        >>>
        """

        if args:
            kwargs.update({"q": args[0]})

        if any(i in RESERVED_KWARGS for i in kwargs):
            raise ValueError(
                "A reserved {} kwarg was passed. Please remove it "
                "try again.".format(RESERVED_KWARGS)
            )

        ret = Request(
            filters=kwargs,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
        )

        return ret.get_count()


class DetailEndpoint:
    """Enables read/write operations on detail endpoints.

    Endpoints like ``available-ips`` that are detail routes off
    traditional endpoints are handled with this class.
    """

    def __init__(self, parent_obj, name, custom_return=None):
        self.parent_obj = parent_obj
        self.custom_return = custom_return
        self.url = "{}/{}/{}/".format(parent_obj.endpoint.url, parent_obj.id, name)
        self.request_kwargs = dict(
            base=self.url,
            token=parent_obj.api.token,
            http_session=parent_obj.api.http_session,
        )

    def list(self, **kwargs):
        r"""The view operation for a detail endpoint

        Returns the response from NetBox for a detail endpoint.

        :args \**kwargs: key/value pairs that get converted into url
            parameters when passed to the endpoint.
            E.g. ``.list(method='get_facts')`` would be converted to
            ``.../?method=get_facts``.

        :returns: A :py:class:`.Record` object or list of :py:class:`.Record` objects created
            from data retrieved from NetBox.
        """
        req = Request(**self.request_kwargs).get(add_params=kwargs)

        if self.custom_return:
            return [
                self.custom_return(
                    i, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                )
                for i in req
            ]
        return req

    def create(self, data=None):
        """The write operation for a detail endpoint.

        Creates objects on a detail endpoint in NetBox.

        :arg dict/list,optional data: A dictionary containing the
            key/value pair of the items you're creating on the parent
            object. Defaults to empty dict which will create a single
            item with default values.

        :returns: A :py:class:`.Record` object or list of :py:class:`.Record` objects created
            from data created in NetBox.
        """
        data = data or {}
        req = Request(**self.request_kwargs).post(data)
        if self.custom_return:
            if isinstance(req, list):
                return [
                    self.custom_return(
                        req_item, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                    )
                    for req_item in req
                ]
            else:
                return self.custom_return(
                    req, self.parent_obj.endpoint.api, self.parent_obj.endpoint
                )
        return req


class RODetailEndpoint(DetailEndpoint):
    def create(self, data):
        raise NotImplementedError("Writes are not supported for this endpoint.")
