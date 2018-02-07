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
import netaddr
import six

from pynetbox.lib.query import Request


def _get_return(lookup, return_fields=['id', 'value', 'nested_return']):

    for i in return_fields:
        if isinstance(lookup, dict) and lookup.get(i):
            return lookup[i]
        else:
            if hasattr(lookup, i):
                return getattr(lookup, i)
    if isinstance(lookup, Record):
        return str(lookup)
    else:
        return lookup


class Record(object):
    """Create python objects from netbox API responses.

        Iterates over `values` and checks if the `key` is defined as a
        a class attribute point to another Record object. If so, it
        then takes `value` and instantiates the referenced object
        creating a nested object of whatever type is requested in the
        class attribute.

        If `key` doesn't match a class attribute an instance attribute
        is set containing `value`.

        :arg dict values: The response from the netbox api.
        :arg dict api_kwargs: Contains the arguments passed to Api()
            when it was instantiated.
    """

    url = None
    has_details = False

    def __init__(self, values, api_kwargs={}, endpoint_meta={}):
        self._full_cache = []
        self._index_cache = []
        self.api_kwargs = api_kwargs
        self.endpoint_meta = endpoint_meta
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
            if self.has_details is False and k != 'keys':
                if self.full_details():
                    ret = getattr(self, k, None)
                    if ret:
                        return ret

        raise AttributeError('object has no attribute "{}"'.format(k))

    def __iter__(self):
        for i in dict(self._full_cache).keys():
            cur_attr = getattr(self, i)
            if isinstance(cur_attr, Record):
                yield i, dict(cur_attr)
            else:
                yield i, cur_attr

    def __getitem__(self, item):
        return item

    def __str__(self):
        return (
            getattr(self, 'name', None) or
            getattr(self, 'label', None) or
            ''
        )

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def _add_cache(self, item):
        key, value = item
        if isinstance(value, Record):
            self._full_cache.append((key, dict(value)))
        else:
            self._full_cache.append((key, value))
        self._index_cache.append((key, _get_return(value)))

    def _parse_values(self, values):
        """ Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """
        for k, v in values.items():
            if k != 'custom_fields':
                if isinstance(v, dict):
                    lookup = getattr(self.__class__, k, None)
                    if lookup:
                        v = lookup(v, api_kwargs=self.api_kwargs)
                    else:
                        v = self.default_ret(v, api_kwargs=self.api_kwargs)
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
        init_dict = {}
        init_vals = dict(self._index_cache)
        for i in dict(self):
            current_val = init_vals.get(i)
            if i != 'custom_fields':
                if isinstance(current_val, dict):
                    init_dict.update({i: _get_return(current_val)})
                else:
                    init_dict.update({i: _get_return(current_val)})
            init_dict.update({i: current_val})
        if init_dict == self.serialize():
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
                token=self.api_kwargs.get('token'),
                session_key=self.api_kwargs.get('session_key'),
                version=self.api_kwargs.get('version')
            )
            self._parse_values(req.get())
            self.has_details = True
            return True
        return False

    def serialize(self, nested=False):
        """Serializes an object

        Pulls all the attributes in an object and creates a dict that
        can be turned into the json that netbox is expecting.

        If an attribute's value is a ``Record`` or ``IPRecord`` type
        it's replaced with the ``id`` field of that object.

        :returns: dict of values the NetBox API is expecting.
        """
        if nested:
            return _get_return(self)

        ret = {}
        for i in dict(self):
            current_val = getattr(self, i)
            if isinstance(current_val, Record):
                current_val = getattr(current_val, 'serialize')(nested=True)

            if isinstance(current_val, netaddr.ip.IPNetwork):
                current_val = str(current_val)

            ret.update({i: current_val})
        return ret

    def save(self):
        """Saves changes to an existing object.

        Runs self.serialize() and checks that it doesn't match
        self._compare(). If not create a Request object and run .put()

        :returns: True if PUT request was successful.
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
            if not self._compare():
                req = Request(
                    key=self.id,
                    base=self.endpoint_meta.get('url'),
                    token=self.api_kwargs.get('token'),
                    session_key=self.api_kwargs.get('session_key'),
                    version=self.api_kwargs.get('version')
                )
                if req.put(self.serialize()):
                    return True
            else:
                return False

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
            base=self.endpoint_meta.get('url'),
            token=self.api_kwargs.get('token'),
            session_key=self.api_kwargs.get('session_key'),
            version=self.api_kwargs.get('version')
        )
        if req.delete():
            return True
        else:
            return False


class IPRecord(Record):
    """IP-specific Record for IPAM responses.

    Extends ``Record`` objects to handle replacing ip4/6 strings with
    instances of ``netaddr.IPNetworks`` instead.
    """

    def __init__(self, *args, **kwargs):
        super(IPRecord, self).__init__(*args, **kwargs)
        self.default_ret = IPRecord

    def __iter__(self):
        for i in dict(self._full_cache).keys():
            cur_attr = getattr(self, i)
            if isinstance(cur_attr, Record):
                yield i, dict(cur_attr)
            else:
                if isinstance(cur_attr, netaddr.IPNetwork):
                    yield i, str(cur_attr)
                else:
                    yield i, cur_attr

    def _parse_values(self, values):
        """ Parses values init arg. for responses with IPs fields.

        Similar parser as parent, but takes str & unicode fields and
        trys converting them to IPNetwork objects.
        """
        for k, v in values.items():
            if k != 'custom_fields':
                if isinstance(v, dict):
                    lookup = getattr(self.__class__, k, None)
                    if lookup:
                        v = lookup(v, api_kwargs=self.api_kwargs)
                    else:
                        v = self.default_ret(v, api_kwargs=self.api_kwargs)
                if isinstance(v, six.string_types):
                    try:
                        v = netaddr.IPNetwork(v)
                    except netaddr.AddrFormatError:
                        pass
                self._add_cache((k, v))
            else:
                self._add_cache((k, v.copy()))
            setattr(self, k, v)
