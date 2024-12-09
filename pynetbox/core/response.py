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

import marshal
from collections import OrderedDict

from pynetbox.core.query import Request
from pynetbox.core.util import Hashabledict

# List of fields that are lists but should be treated as sets.
LIST_AS_SET = ("tags", "tagged_vlans")


def get_foreign_key(record):
    """
    Get the foreign key for Record objects and dictionaries.
    """
    if isinstance(record, dict):
        gfk = record.get("id", None) or record.get("value", None)
    elif isinstance(record, Record):
        gfk = getattr(record, "id", None) or getattr(record, "value", None)
    return gfk


def flatten_custom(custom_dict):
    ret = {}

    for k, val in custom_dict.items():
        current_val = val

        if isinstance(val, dict):
            current_val = val.get("id", val)

        if isinstance(val, list):
            current_val = [v.get("id", v) if isinstance(v, dict) else v for v in val]

        ret[k] = current_val
    return ret


class JsonField:
    """Explicit field type for values that are not to be converted
    to a Record object"""

    _json_field = True


class CachedRecordRegistry:
    """
    A cache for Record objects.
    """

    def __init__(self, api):
        self.api = api
        self._cache = {}
        self._hit = 0
        self._miss = 0

    def get(self, object_type, key):
        """
        Retrieves a record from the cache
        """
        return self._cache.get(object_type, {}).get(key, None)

    def set(self, object_type, key, value):
        """
        Stores a record in the cache
        """
        if object_type not in self._cache:
            self._cache[object_type] = {}
        self._cache[object_type][key] = value


class RecordSet:
    """Iterator containing Record objects.

    Returned by :py:meth:`.Endpoint.all()` and :py:meth:`.Endpoint.filter()` methods.
    Allows iteration of and actions to be taken on the results from the aforementioned
    methods. Contains :py:class:`.Record` objects.

    :Examples:

    To see how many results are in a query by calling ``len()``:

    >>> x = nb.dcim.devices.all()
    >>> len(x)
    123
    >>>

    Simple iteration of the results:

    >>> devices = nb.dcim.devices.all()
    >>> for device in devices:
    ...     print(device.name)
    ...
    test1-leaf1
    test1-leaf2
    test1-leaf3
    >>>

    """

    def __init__(self, endpoint, request, **kwargs):
        self.endpoint = endpoint
        self.request = request
        self.response = self.request.get()
        self._response_cache = []
        self._init_endpoint_cache()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self._response_cache:
                return self.endpoint.return_obj(
                    self._response_cache.pop(),
                    self.endpoint.api,
                    self.endpoint,
                )
            return self.endpoint.return_obj(
                next(self.response),
                self.endpoint.api,
                self.endpoint,
            )
        except StopIteration:
            self._clear_endpoint_cache()
            raise

    def _init_endpoint_cache(self):
        self.endpoint._cache = CachedRecordRegistry(self.endpoint.api)

    def _clear_endpoint_cache(self):
        self.endpoint._cache = None

    def __len__(self):
        try:
            return self.request.count
        except AttributeError:
            try:
                self._response_cache.append(next(self.response))
            except StopIteration:
                return 0
            return self.request.count

    def update(self, **kwargs):
        """Updates kwargs onto all Records in the RecordSet and saves these.

        Updates are only sent to the API if a value were changed, and only for
        the Records which were changed

        :returns: True if the update succeeded, None if no update were required
        :example:

        >>> result = nb.dcim.devices.filter(site_id=1).update(status='active')
        True
        >>>
        """
        updates = []
        for record in self:
            # Update each record and determine if anything was updated
            for k, v in kwargs.items():
                setattr(record, k, v)
            record_updates = record.updates()
            if record_updates:
                # if updated, add the id to the dict and append to list of updates
                record_updates["id"] = record.id
                updates.append(record_updates)
        if updates:
            return self.endpoint.update(updates)
        else:
            return None

    def delete(self):
        r"""Bulk deletes objects in a RecordSet.

        Allows for batch deletion of multiple objects in a RecordSet

        :returns: True if bulk DELETE operation was successful.

        :Examples:

        Deleting offline `devices` on site 1:

        >>> netbox.dcim.devices.filter(site_id=1, status="offline").delete()
        >>>
        """
        return self.endpoint.delete(self)


class BaseRecord:
    def __init__(self):
        self._init_cache = []

    def __getitem__(self, k):
        return dict(self)[k]

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)


class ValueRecord(BaseRecord):
    def __init__(self, values, *args, **kwargs):
        super().__init__()
        if values:
            self._parse_values(values)

    def __iter__(self):
        for k, _ in self._init_cache:
            cur_attr = getattr(self, k)
            yield k, cur_attr

    def __repr__(self):
        return getattr(self, "label", "")

    @property
    def _key(self):
        return getattr(self, "value")

    def __eq__(self, other):
        if isinstance(other, ValueRecord):
            return self._foreign_key == other._foreign_key
        return NotImplemented

    def _parse_values(self, values):
        for k, v in values.items():
            self._init_cache.append((k, v))
            setattr(self, k, v)

    def serialize(self, nested=False):
        return self._key if nested else dict(self)


class Record(BaseRecord):
    """Create Python objects from NetBox API responses.

    Creates an object from a NetBox response passed as ``values``.
    Nested dicts that represent other endpoints are also turned
    into ``Record`` objects. All fields are then assigned to the
    object's attributes. If a missing attr is requested
    (e.g. requesting a field that's only present on a full response on
    a ``Record`` made from a nested response) then pynetbox will make a
    request for the full object and return the requested value.

    :examples:

    Default representation of the object is usually its name:

    >>> x = nb.dcim.devices.get(1)
    >>> x
    test1-switch1
    >>>

    Querying a string field:

    >>> x = nb.dcim.devices.get(1)
    >>> x.serial
    'ABC123'
    >>>

    Querying a field on a nested object:

    >>> x = nb.dcim.devices.get(1)
    >>> x.device_type.model
    'QFX5100-24Q'
    >>>

    Casting the object as a dictionary:

    >>> from pprint import pprint
    >>> pprint(dict(x))
    {'asset_tag': None,
     'cluster': None,
     'comments': '',
     'config_context': {},
     'created': '2018-04-01',
     'custom_fields': {},
     'role': {'id': 1,
                     'name': 'Test Switch',
                     'slug': 'test-switch',
                     'url': 'http://localhost:8000/api/dcim/device-roles/1/'},
     'device_type': {...},
     'display_name': 'test1-switch1',
     'face': {'label': 'Rear', 'value': 1},
     'id': 1,
     'name': 'test1-switch1',
     'parent_device': None,
     'platform': {...},
     'position': 1,
     'primary_ip': {'address': '192.0.2.1/24',
                    'family': 4,
                    'id': 1,
                    'url': 'http://localhost:8000/api/ipam/ip-addresses/1/'},
     'primary_ip4': {...},
     'primary_ip6': None,
     'rack': {'display_name': 'Test Rack',
              'id': 1,
              'name': 'Test Rack',
              'url': 'http://localhost:8000/api/dcim/racks/1/'},
     'serial': 'ABC123',
     'site': {'id': 1,
              'name': 'TEST',
              'slug': 'TEST',
              'url': 'http://localhost:8000/api/dcim/sites/1/'},
     'status': {'label': 'Active', 'value': 1},
     'tags': [],
     'tenant': None,
     'vc_position': None,
     'vc_priority': None,
     'virtual_chassis': None}
     >>>

     Iterating over a ``Record`` object:

    >>> for i in x:
    ...  print(i)
    ...
    ('id', 1)
    ('name', 'test1-switch1')
    ('display_name', 'test1-switch1')
    >>>

    """

    def __init__(self, values, api, endpoint):
        self.has_details = False
        super().__init__()
        self.api = api
        self.default_ret = Record
        self.url = values.get("url", None) if values else None
        self._endpoint = endpoint
        if values:
            self._parse_values(values)

    def __getattr__(self, k):
        """Default behavior for missing attrs.

        We'll call `full_details()` if we're asked for an attribute
        we don't have.

        In order to prevent non-explicit behavior,`k='keys'` is
        excluded because casting to dict() calls this attr.
        """
        if self.url:
            if self.has_details is False and k != "keys":
                if self.full_details():
                    ret = getattr(self, k, None)
                    if ret or hasattr(self, k):
                        return ret

        raise AttributeError('object has no attribute "{}"'.format(k))

    def __iter__(self):
        for k, _ in self._init_cache:
            cur_attr = getattr(self, k)
            if isinstance(cur_attr, Record):
                yield k, dict(cur_attr)
            elif isinstance(cur_attr, list) and all(
                isinstance(i, Record) for i in cur_attr
            ):
                yield k, [dict(x) for x in cur_attr]
            else:
                yield k, cur_attr

    def __str__(self):
        return (
            getattr(self, "name", None)
            or getattr(self, "label", None)
            or getattr(self, "display", None)
            or ""
        )

    def __key__(self):
        if hasattr(self, "id"):
            return (self.endpoint.name, self.id)
        else:
            return self.endpoint.name

    def __hash__(self):
        return hash(self.__key__())

    def __eq__(self, other):
        if isinstance(other, Record):
            return self.__key__() == other.__key__()
        return NotImplemented

    @property
    def endpoint(self):
        if self._endpoint is None:
            self._endpoint = self._endpoint_from_url()
        return self._endpoint

    def _endpoint_from_url(self):
        url_path = self.url.replace(self.api.base_url, "").split("/")
        is_plugin = url_path and url_path[1] == "plugins"
        start = 2 if is_plugin else 1
        app, name = [i.replace("-", "_") for i in url_path[start : start + 2]]
        if is_plugin:
            return getattr(getattr(self.api.plugins, app), name)
        else:
            return getattr(getattr(self.api, app), name)

    def _get_or_init(self, object_type, key, value, model):
        """
        Returns a record from the endpoint cache if it exists, otherwise
        initializes a new record, store it in the cache, and return it.
        """
        if key and self._endpoint and self._endpoint._cache:
            if cached := self._endpoint._cache.get(object_type, key):
                self._endpoint._cache._hit += 1
                return cached
        record = model(value, self.api, None)
        if key and self._endpoint and self._endpoint._cache:
            self._endpoint._cache._miss += 1
            self._endpoint._cache.set(object_type, key, record)
        return record

    def _parse_values(self, values):
        """Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """

        non_record_dict_fields = ["custom_fields", "local_context_data"]

        def deep_copy(value):
            return marshal.loads(marshal.dumps(value))

        def dict_parser(key_name, value, model=None):
            if key_name in non_record_dict_fields:
                return value, deep_copy(value)

            if model is None:
                model = getattr(self.__class__, key_name, None)

            if model and issubclass(model, JsonField):
                return value, deep_copy(value)

            if id := value.get("id", None):
                # if model or "url" in value:
                if url := value.get("url", None):
                    model = model or Record
                    value = self._get_or_init(key_name, url, value, model)
                    return value, id

            if record_value := value.get("value", None):
                # if set(value.keys()) == {"value", "label"}:
                # value = ValueRecord(values)
                value = self._get_or_init(key_name, record_value, value, ValueRecord)
                return value, record_value

            return value, deep_copy(value)

        def mixed_list_parser(value):
            from pynetbox.models.mapper import CONTENT_TYPE_MAPPER

            parsed_list = []
            for item in value:
                lookup = item["object_type"]
                if model := CONTENT_TYPE_MAPPER.get(lookup, None):
                    item = self._get_or_init(
                        lookup, item["object"]["url"], item["object"], model
                    )
                parsed_list.append(item)
            return parsed_list

        def list_parser(key_name, value):
            if not value:
                return [], []

            if key_name in ["constraints"]:
                return value, deep_copy(value)

            sample_item = value[0]
            if not isinstance(sample_item, dict):
                return value, [*value]

            is_mixed_list = "object_type" in sample_item and "object" in sample_item
            if is_mixed_list:
                value = mixed_list_parser(value)
            else:
                lookup = getattr(self.__class__, key_name, None)
                model = lookup[0] if isinstance(lookup, list) else self.default_ret
                value = [dict_parser(key_name, i, model=model)[0] for i in value]

            return value, [*value]

        def parse_value(key_name, value):
            if isinstance(value, dict):
                value, to_cache = dict_parser(key_name, value)
            elif isinstance(value, list):
                value, to_cache = list_parser(key_name, value)
            else:
                to_cache = value
            setattr(self, key_name, value)
            return to_cache

        self._init_cache = [(k, parse_value(k, v)) for k, v in values.items()]

    def full_details(self):
        """Queries the hyperlinked endpoint if 'url' is defined.

        This method will populate the attributes from the detail
        endpoint when it's called. Sets the class-level `has_details`
        attribute when it's called to prevent being called more
        than once.

        :returns: True
        """
        if self.url:
            req = Request(
                base=self.url,
                token=self.api.token,
                http_session=self.api.http_session,
            )
            self._parse_values(next(req.get()))
            self.has_details = True
            return True
        return False

    def serialize(self, nested=False, init=False):
        """Serializes an object

        Pulls all the attributes in an object and creates a dict that
        can be turned into the json that netbox is expecting.

        If an attribute's value is a ``Record`` type it's replaced with
        the ``id`` field of that object.

        .. note::

            Using this to get a dictionary representation of the record
            is discouraged. It's probably better to cast to dict()
            instead. See Record docstring for example.

        :returns: dict.
        """
        if nested:
            return getattr(self, "id")

        if init:
            init_vals = dict(self._init_cache)

        ret = {}
        for i in dict(self):
            current_val = getattr(self, i) if not init else init_vals.get(i)
            if i == "custom_fields":
                ret[i] = flatten_custom(current_val)
            else:
                if isinstance(current_val, BaseRecord):
                    current_val = getattr(current_val, "serialize")(nested=True)

                if isinstance(current_val, list):
                    current_val = [
                        v.id if isinstance(v, Record) else v for v in current_val
                    ]
                    if i in LIST_AS_SET and (
                        all([isinstance(v, str) for v in current_val])
                        or all([isinstance(v, int) for v in current_val])
                    ):
                        current_val = list(OrderedDict.fromkeys(current_val))
                ret[i] = current_val
        return ret

    def _diff(self):
        def fmt_dict(k, v):
            if isinstance(v, dict):
                return k, Hashabledict(v)
            if isinstance(v, list):
                return k, ",".join(map(str, v))
            return k, v

        current = Hashabledict({fmt_dict(k, v) for k, v in self.serialize().items()})
        init = Hashabledict(
            {fmt_dict(k, v) for k, v in self.serialize(init=True).items()}
        )
        return set([i[0] for i in set(current.items()) ^ set(init.items())])

    def updates(self):
        """Compiles changes for an existing object into a dict.

        Takes a diff between the objects current state and its state at init
        and returns them as a dictionary, which will be empty if no changes.

        :returns: dict.
        :example:

        >>> x = nb.dcim.devices.get(name='test1-a3-tor1b')
        >>> x.serial
        ''
        >>> x.serial = '1234'
        >>> x.updates()
        {'serial': '1234'}
        >>>
        """
        if self.id:
            diff = self._diff()
            if diff:
                serialized = self.serialize()
                return {i: serialized[i] for i in diff}
        return {}

    def save(self):
        """Saves changes to an existing object.

        Takes a diff between the objects current state and its state at init
        and sends them as a dictionary to Request.patch().

        :returns: True if PATCH request was successful.
        :example:

        >>> x = nb.dcim.devices.get(name='test1-a3-tor1b')
        >>> x.serial
        ''
        >>> x.serial = '1234'
        >>> x.save()
        True
        >>>
        """
        updates = self.updates()
        if updates:
            req = Request(
                key=self.id,
                base=self.endpoint.url,
                token=self.api.token,
                http_session=self.api.http_session,
            )
            if req.patch(updates):
                return True
        return False

    def update(self, data):
        """Update an object with a dictionary.

        Accepts a dict and uses it to update the record and call save().
        For nested and choice fields you'd pass an int the same as
        if you were modifying the attribute and calling save().

        :arg dict data: Dictionary containing the k/v to update the
            record object with.
        :returns: True if PATCH request was successful.
        :example:

        >>> x = nb.dcim.devices.get(1)
        >>> x.update({
        ...   "name": "test-switch2",
        ...   "serial": "ABC321",
        ... })
        True

        """

        for k, v in data.items():
            setattr(self, k, v)
        return self.save()

    def delete(self):
        """Deletes an existing object.

        :returns: True if DELETE operation was successful.
        :example:

        >>> x = nb.dcim.devices.get(name='test1-a3-tor1b')
        >>> x.delete()
        True
        >>>
        """
        req = Request(
            key=self.id,
            base=self.endpoint.url,
            token=self.api.token,
            http_session=self.api.http_session,
        )
        return True if req.delete() else False
