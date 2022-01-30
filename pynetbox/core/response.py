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
import copy
from collections import OrderedDict

import pynetbox.core.app
from six.moves.urllib.parse import urlsplit
from pynetbox.core.query import Request, RequestError
from pynetbox.core.util import Hashabledict


# List of fields that are lists but should be treated as sets.
LIST_AS_SET = ("tags", "tagged_vlans")


def get_return(lookup, return_fields=None):
    """Returns simple representations for items passed to lookup.

    Used to return a "simple" representation of objects and collections
    sent to it via lookup. Otherwise, we look to see if
    lookup is a "choices" field (dict with only 'id' and 'value')
    or a nested_return. Finally, we check if it's a Record, if
    so simply return a string. Order is important due to nested_return
    being self-referential.

    :arg list,optional return_fields: A list of fields to reference when
        calling values on lookup.
    """

    for i in return_fields or ["id", "value", "nested_return"]:
        if isinstance(lookup, dict) and lookup.get(i):
            return lookup[i]
        else:
            if hasattr(lookup, i):
                # check if this is a "choices" field record
                # from a NetBox 2.7 server.
                if sorted(dict(lookup)) == sorted(["id", "value", "label"]):
                    return getattr(lookup, "value")
                return getattr(lookup, i)

    if isinstance(lookup, Record):
        return str(lookup)
    else:
        return lookup


def flatten_custom(custom_dict):
    return {
        k: v if not isinstance(v, dict) else v["value"] for k, v in custom_dict.items()
    }


class JsonField(object):
    """Explicit field type for values that are not to be converted
    to a Record object"""

    _json_field = True


class RecordSet(object):
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

    def __iter__(self):
        return self

    def __next__(self):
        if self._response_cache:
            return self.endpoint.return_obj(
                self._response_cache.pop(), self.endpoint.api, self.endpoint
            )
        return self.endpoint.return_obj(
            next(self.response), self.endpoint.api, self.endpoint
        )

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


class Record(object):
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
     'device_role': {'id': 1,
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

    url = None

    def __init__(self, values, api, endpoint):
        self.has_details = False
        self._full_cache = []
        self._init_cache = []
        self.api = api
        self.default_ret = Record
        self.endpoint = (
            self._endpoint_from_url(values["url"])
            if values and "url" in values
            else endpoint
        )
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
        for i in dict(self._init_cache):
            cur_attr = getattr(self, i)
            if isinstance(cur_attr, Record):
                yield i, dict(cur_attr)
            elif isinstance(cur_attr, list) and all(
                isinstance(i, Record) for i in cur_attr
            ):
                yield i, [dict(x) for x in cur_attr]
            else:
                yield i, cur_attr

    def __getitem__(self, k):
        return dict(self)[k]

    def __str__(self):
        return (
            getattr(self, "name", None)
            or getattr(self, "label", None)
            or getattr(self, "display", None)
            or ""
        )

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

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

    def _add_cache(self, item):
        key, value = item
        self._init_cache.append((key, get_return(value)))

    def _parse_values(self, values):
        """Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """

        def list_parser(key_name, list_item):
            if isinstance(list_item, dict):
                lookup = getattr(self.__class__, key_name, None)
                if not isinstance(lookup, list):
                    # This is *list_parser*, so if the custom model field is not
                    # a list (or is not defined), just return the default model
                    return self.default_ret(list_item, self.api, self.endpoint)
                else:
                    model = lookup[0]
                    return model(list_item, self.api, self.endpoint)
            return list_item

        for k, v in values.items():
            if isinstance(v, dict):
                lookup = getattr(self.__class__, k, None)
                if k in ["custom_fields", "local_context_data"] or hasattr(
                    lookup, "_json_field"
                ):
                    self._add_cache((k, copy.deepcopy(v)))
                    setattr(self, k, v)
                    continue
                if lookup:
                    v = lookup(v, self.api, self.endpoint)
                else:
                    v = self.default_ret(v, self.api, self.endpoint)
                self._add_cache((k, v))

            elif isinstance(v, list):
                v = [list_parser(k, i) for i in v]
                to_cache = list(v)
                self._add_cache((k, to_cache))

            else:
                self._add_cache((k, v))
            setattr(self, k, v)

    def _endpoint_from_url(self, url):
        url_path = urlsplit(url).path
        base_url_path_parts = urlsplit(self.api.base_url).path.split("/")
        if len(base_url_path_parts) > 2:
            # There are some extra directories in the path, remove them from url
            extra_path = "/".join(base_url_path_parts[:-1])
            url_path = url_path[len(extra_path) :]
        split_url_path = url_path.split("/")
        if split_url_path[2] == "plugins":
            # Skip plugins from the path
            app, name = split_url_path[3:5]
        else:
            app, name = split_url_path[2:4]
        return getattr(pynetbox.core.app.App(self.api, app), name)

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
                session_key=self.api.session_key,
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
            return get_return(self)

        if init:
            init_vals = dict(self._init_cache)

        ret = {}
        for i in dict(self):
            current_val = getattr(self, i) if not init else init_vals.get(i)
            if i == "custom_fields":
                ret[i] = flatten_custom(current_val)
            else:
                if isinstance(current_val, Record):
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
        u''
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
        u''
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
                session_key=self.api.session_key,
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
            session_key=self.api.session_key,
            http_session=self.api.http_session,
        )
        return True if req.delete() else False
