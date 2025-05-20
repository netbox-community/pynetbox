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

    ## Parameters

    * **api** (Api): Takes Api created at instantiation.
    * **app** (App): Takes App.
    * **name** (str): Name of endpoint passed to App().
    * **model** (obj, optional): Custom model for given app.

    ## Note

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

        ## Parameters

        * **name** (str): Endpoint name.
        * **model** (obj): The application model that contains unique Record objects.

        ## Returns
        Record (obj)
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

        ## Parameters

        * **limit** (int, optional): Overrides the max page size on
            paginated returns. This defines the number of records that will
            be returned with each query to the Netbox server. The queries
            will be made as you iterate through the result set.
        * **offset** (int, optional): Overrides the offset on paginated returns.

        ## Returns
        A RecordSet object.

        ## Examples

        ```python
        devices = list(nb.dcim.devices.all())
        for device in devices:
            print(device.name)

        # test1-leaf1
        # test1-leaf2
        # test1-leaf3
        ```

        If you want to iterate over the results multiple times then
        encapsulate them in a list like this:
        ```python
        devices = list(nb.dcim.devices.all())
        ```

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
        """Queries the DetailsView of a given endpoint.

        ## Parameters

        * **key** (int, optional): id for the item to be retrieved.
        * **kwargs**: Accepts the same keyword args as filter(). Any search argument the endpoint accepts can
            be added as a keyword arg.

        ## Returns
        A single Record object or None

        ## Raises
        ValueError: if kwarg search return more than one value.

        ## Examples

        Referencing with a kwarg that only returns one value:

        ```python
        nb.dcim.devices.get(name='test1-a3-tor1b')
        # test1-a3-tor1b
        ```

        Referencing with an id:

        ```python
        nb.dcim.devices.get(1)
        # test1-edge1
        ```

        Using multiple named arguments. For example, retrieving the location when the location name is not unique and used in multiple sites:

        ```python
        nb.locations.get(site='site-1', name='Row 1')
        # Row 1
        ```
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
        """Queries the 'ListView' of a given endpoint.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it.

        ## Parameters

        * **args** (str, optional): Freeform search string that's
            accepted on given endpoint.
        * **kwargs** (str, optional): Any search argument the
            endpoint accepts can be added as a keyword arg.
        * **limit** (int, optional): Overrides the max page size on
            paginated returns. This defines the number of records that will
            be returned with each query to the Netbox server. The queries
            will be made as you iterate through the result set.
        * **offset** (int, optional): Overrides the offset on paginated returns.

        ## Returns
        A RecordSet object.

        ## Examples

        To return a list of objects matching a named argument filter:

        ```python
        devices = nb.dcim.devices.filter(role='leaf-switch')
        for device in devices:
            print(device.name)

        # test1-leaf1
        # test1-leaf2
        # test1-leaf3
        ```

        ```python
        devices = nb.dcim.devices.filter(site='site-1')
        for device in devices:
            print(device.name)

        # test1-a2-leaf1
        # test2-a2-leaf2
        ```

        ## Note

        If a keyword argument is incorrect a `TypeError` will not be returned by pynetbox.
        Instead, all records filtered up to the last correct keyword argument. For example, if we used `site="Site 1"` instead of `site=site-1` when using filter on
        the devices endpoint, then pynetbox will return **all** devices across all sites instead of devices at Site 1.

        Using a freeform query along with a named argument:

        ```python
        devices = nb.dcim.devices.filter('a3', role='leaf-switch')
        for device in devices:
            print(device.name)

        # test1-a3-leaf1
        # test1-a3-leaf2
        ```
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
        filters = {x: y if y is not None else "null" for x, y in kwargs.items()}
        req = Request(
            filters=filters,
            base=self.url,
            token=self.token,
            http_session=self.api.http_session,
            threading=self.api.threading,
            limit=limit,
            offset=offset,
        )

        return RecordSet(self, req)

    def create(self, *args, **kwargs):
        """Creates an object on an endpoint.

        Takes named arguments that match the given endpoint's
        available fields. Returns a new object.

        ## Parameters

        * **args**: Not used.
        * **kwargs**: Fields and values to create the object with.

        ## Returns
        A Record object.

        ## Examples

        Creating a new device:

        ```python
        new_device = nb.dcim.devices.create(
            name='test-device',
            device_type=1,
            device_role=1,
            site=1
        )
        ```

        Creating a new device with a nested object:

        ```python
        new_device = nb.dcim.devices.create(
            name='test-device',
            device_type={'id': 1},
            device_role={'id': 1},
            site={'id': 1}
        )
        ```
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
        """Updates objects in NetBox.

        Takes a list of objects and updates them in NetBox.

        ## Parameters

        * **objects** (list): A list of Record objects to update.

        ## Returns
        A list of Record objects.

        ## Examples

        ```python
        devices = nb.dcim.devices.filter(site='test1')
        for device in devices:
            device.status = 'active'
        nb.dcim.devices.update(devices)
        ```
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
        """Deletes objects from NetBox.

        Takes a list of objects and deletes them from NetBox.

        ## Parameters

        * **objects** (list): A list of Record objects to delete.

        ## Returns
        True if the delete operation was successful.

        ## Examples

        ```python
        devices = nb.dcim.devices.filter(site='test1')
        nb.dcim.devices.delete(devices)
        ```
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
        """Returns all choices from the endpoint if it has them.

        ## Returns
        Dictionary of available choices.

        ## Examples

        ```python
        choices = nb.dcim.devices.choices()
        print(choices['status'])
        {
            'label': 'Active',
            'value': 'active'
        }
        ```
        """
        if self._choices:
            return self._choices

        req = Request(
            base=self.url,
            token=self.api.token,
            http_session=self.api.http_session,
        ).options()

        actions = req.get("actions", {})
        post_data = actions.get("POST") or actions.get("PUT")
        if post_data is None:
            raise ValueError(
                "Unexpected format in the OPTIONS response at {}".format(self.url)
            )
        self._choices = {}
        for prop in post_data:
            if "choices" in post_data[prop]:
                self._choices[prop] = post_data[prop]["choices"]

        return self._choices

    def count(self, *args, **kwargs):
        """Returns the count of objects in a query.

        Takes named arguments that match the usable filters on a
        given endpoint. If an argument is passed then it's used as a
        freeform search argument if the endpoint supports it.

        ## Parameters

        * **args** (str, optional): Freeform search string that's
            accepted on given endpoint.
        * **kwargs** (str, optional): Any search argument the
            endpoint accepts can be added as a keyword arg.

        ## Returns
        Integer of count of objects.

        ## Examples

        ```python
        nb.dcim.devices.count(site='test1')
        # 27
        ```
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

    Endpoints like `available-ips` that are detail routes off
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
        """The view operation for a detail endpoint.

        Returns the response from NetBox for a detail endpoint.

        ## Parameters

        * **kwargs**: Key/value pairs that get converted into URL
            parameters when passed to the endpoint.
            E.g. `.list(method='get_facts')` would be converted to
            `.../?method=get_facts`.

        ## Returns
        A Record object or list of Record objects created
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

        ## Parameters

        * **data** (dict/list, optional): A dictionary containing the
            key/value pair of the items you're creating on the parent
            object. Defaults to empty dict which will create a single
            item with default values.

        ## Returns
        A Record object or list of Record objects created
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
