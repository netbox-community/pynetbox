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

from pynetbox.lib.query import Request


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
        self._meta = []
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
        This was done in order to prevent non-explicit API calls.
        """
        if self.url:
            if self.has_details is False and k != 'keys':
                if self.full_details():
                    ret = getattr(self, k, None)
                    if ret:
                        return ret

        raise AttributeError('object has no attribute "{}"'.format(k))

    def __iter__(self):
        for i in dict(self._meta).keys():
            cur_attr = getattr(self, i)
            if isinstance(cur_attr, (int, basestring, type(None), list)):
                yield i, cur_attr
            else:
                yield i, dict(cur_attr)

    def __getitem__(self, item):
        return item

    def __str__(self):
        return self.name or ''

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def _parse_values(self, values):
        """ Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """
        for k, v in values.items():
            self._meta.append((k, v))
            if isinstance(v, dict) and k != 'custom_fields':
                lookup = getattr(self.__class__, k, None)
                if lookup:
                    setattr(self, k, lookup(v, api_kwargs=self.api_kwargs))
                else:
                    setattr(
                        self,
                        k,
                        self.default_ret(v, api_kwargs=self.api_kwargs)
                    )
            else:
                setattr(self, k, v)

    def _compare(self):
        """Compares current attributes to values at instantiation.

        In order to be idempotent we run this method in `save()`.

        Returns:
            Boolean value, True indicates current instance has the same
            attributes as the ones passed to `values`.
        """
        init_dict = {}
        init_vals = dict(self._meta)
        for i in dict(self):
            if i != 'custom_fields':
                current_val = init_vals.get(i)
                if isinstance(current_val, dict):
                    current_val_id = current_val.get('id')
                    current_val_value = current_val.get('value')
                    init_dict.update(
                        {i: current_val_id or current_val_value}
                    )
                else:
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
                version=self.api_kwargs.get('version')
            )
            self._parse_values(req.get())
            self.has_details = True
            return True
        return False

    def serialize(self):
        """Serializes an object

        Pulls all the attributes in an object and creates a dict that
        can be turned into the json that netbox is expecting.

        :returns: dict of values the NetBox API is expecting.
        """
        ret = {}
        for i in dict(self):
            current_val = getattr(self, i)
            if i != 'custom_fields':
                try:
                    current_val = current_val.id
                except AttributeError:
                    type_filter = (int, basestring, type(None))
                    if not isinstance(current_val, type_filter):
                        current_val = current_val.value
            ret.update({i: current_val})
        return ret

    def save(self):
        """Saves changes to an existing object.

        Runs self.serialize() and checks that it doesn't match
        self._compare(). If not create a Request object and run .put()

        :returns: True if PUT request was successful.
        :example:

        >>> x = nb.devices.get(name='test1-a3-tor1b')
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

        >>> x = nb.devices.get(name='test1-a3-tor1b')
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
        for i in dict(self._meta).keys():
            cur_attr = getattr(self, i)
            if isinstance(cur_attr, (int, basestring, type(None))):
                yield i, cur_attr
            else:
                if isinstance(cur_attr, netaddr.IPNetwork):
                    yield i, str(cur_attr)
                else:
                    yield i, dict(cur_attr)

    def _parse_values(self, values):
        """ Parses values init arg. for responses with IPs fields.

        Similar parser as parent, but takes basestring fields and trys
        converting them to IPNetwork objects.
        """
        for k, v in values.items():
            self._meta.append((k, v))
            if isinstance(v, dict) and k != 'custom_fields':
                lookup = getattr(self.__class__, k, None)
                if lookup:
                    setattr(self, k, lookup(v, api_kwargs=self.api_kwargs))
                else:
                    setattr(
                        self,
                        k,
                        self.default_ret(v, api_kwargs=self.api_kwargs)
                    )
            else:
                if isinstance(v, basestring):
                    try:
                        v = netaddr.IPNetwork(v)
                    except netaddr.AddrFormatError:
                        pass
                setattr(self, k, v)

    def serialize(self):
        """Serializes an IPRecord object

        Pulls all the attributes in an object and creates a dict that
        can be turned into the json that netbox is expecting. Also
        accounts for IPNetwork objects present in IPRecord objects.

        :returns: dict of values the NetBox API is expecting.
        """
        ret = {}
        for i in dict(self):
            current_val = getattr(self, i)
            if i != 'custom_fields':
                try:
                    current_val = current_val.id
                except AttributeError:
                    type_filter = (int, basestring, type(None))
                    if not isinstance(current_val, type_filter):
                        if isinstance(current_val, netaddr.ip.IPNetwork):
                            current_val = str(current_val)
                        else:
                            current_val = current_val.value
            ret.update({i: current_val})
        return ret


class BoolRecord(Record):
    """Simple boolean record type to handle NetBox responses with fields
    containing json objects that aren't a reference to another endpoint.

    E.g. status field on device response.
    """

    def __str__(self):
        return self.label
