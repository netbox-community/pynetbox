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
from pynetbox.core.query import Request
from pynetbox.core.util import Hashabledict

# List of fields that contain a dict but are not to be converted into
# Record objects.
JSON_FIELDS = ("custom_fields", "data", "config_context")


def get_return(lookup, return_fields=None):
    """Returns simple representations for items passed to lookup.

    Used to return a "simple" representation of objects and collections
    sent to it via lookup. If lookup is an IPNetwork object immediately
    return the string representation. Otherwise, we look to see if
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
                return getattr(lookup, i)

    if isinstance(lookup, Record):
        return str(lookup)
    else:
        return lookup


def flatten_custom(custom_dict):
    return {
        k: v if not isinstance(v, dict) else v["value"]
        for k, v in custom_dict.items()
    }


class Record(object):
    """Create python objects from netbox API responses.

    Creates an object from a NetBox response passed as `values`.
    Nested dicts that represent other endpoints are also turned
    into Record objects. All fields are then assigned to the
    object's attributes. If a missing attr is requested
    (e.g. requesting a field that's only present on a full response on
    a Record made from a nested response) the pynetbox will make a
    request for the full object and return the requsted value.

    :examples:

    Default representation of the object is usually its name

    >>> x = nb.dcim.devices.get(1)
    >>> x
    test1-switch1
    >>>

    Querying a string field.

    >>> x = nb.dcim.devices.get(1)
    >>> x.serial
    'ABC123'
    >>>

    Querying a field on a nested object.

    >>> x = nb.dcim.devices.get(1)
    >>> x.device_type.model
    'QFX5100-24Q'
    >>>

    Casting the object as a dictionary.

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

     Iterating over a Record object.

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
        self.endpoint = endpoint
        self.default_ret = Record

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
            else:
                yield i, cur_attr

    def __getitem__(self, item):
        return item

    def __str__(self):
        return (
            getattr(self, "name", None) or getattr(self, "label", None) or ""
        )

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def _add_cache(self, item):
        key, value = item
        self._init_cache.append((key, get_return(value)))

    def _parse_values(self, values):
        """ Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """

        def list_parser(list_item):
            if isinstance(list_item, dict):
                return self.default_ret(list_item, self.api, self.endpoint)
            return list_item

        for k, v in values.items():

            if k not in JSON_FIELDS:
                if isinstance(v, dict):
                    lookup = getattr(self.__class__, k, None)
                    if lookup:
                        v = lookup(v, self.api, self.endpoint)
                    else:
                        v = self.default_ret(v, self.api, self.endpoint)
                    self._add_cache((k, v))

                elif isinstance(v, list):
                    v = [list_parser(i) for i in v]
                    to_cache = list(v)
                    self._add_cache((k, to_cache))

                else:
                    self._add_cache((k, v))
            else:
                self._add_cache((k, v.copy()))
            setattr(self, k, v)

    def _compare(self):
        """Compares current attributes to values at instantiation.

        In order to be idempotent we run this method in `save()`.

        Returns:
            Boolean value, True indicates current instance has the same
            attributes as the ones passed to `values`.
        """

        if self.serialize(init=True) == self.serialize():
            return True
        return False

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
                ssl_verify=self.api.ssl_verify,
            )
            self._parse_values(req.get())
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
            elif i == "tags":
                ret[i] = list(set(current_val))
            else:
                if isinstance(current_val, Record):
                    current_val = getattr(current_val, "serialize")(
                        nested=True
                    )

                if isinstance(current_val, list):
                    current_val = [
                        v.id if isinstance(v, Record) else v
                        for v in current_val
                    ]
                ret[i] = current_val
        return ret

    def _diff(self):
        def fmt_dict(k, v):
            if isinstance(v, dict):
                return k, Hashabledict(v)
            if isinstance(v, list):
                return k, "".join(map(str, v))
            return k, v

        current = Hashabledict(
            {fmt_dict(k, v) for k, v in self.serialize().items()}
        )
        init = Hashabledict(
            {fmt_dict(k, v) for k, v in self.serialize(init=True).items()}
        )
        return set([i[0] for i in set(current.items()) ^ set(init.items())])

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
        if self.id:
            diff = self._diff()
            if diff:
                serialized = self.serialize()
                req = Request(
                    key=self.id,
                    base=self.endpoint.url,
                    token=self.api.token,
                    session_key=self.api.session_key,
                    ssl_verify=self.api.ssl_verify,
                )
                if req.patch({i: serialized[i] for i in diff}):
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
            ssl_verify=self.api.ssl_verify,
        )
        return True if req.delete() else False
