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
from pynetbox.core.response import Record
from pynetbox.core.endpoint import DetailEndpoint


class IpAddresses(Record):
    def __str__(self):
        return str(self.address)


class Prefixes(Record):
    def __str__(self):
        return str(self.prefix)

    @property
    def available_ips(self):
        """Represents the ``available-ips`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing and creating IP addresses inside a prefix.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> prefix = nb.ipam.prefixes.get(24)
        >>> prefix.available_ips.list()
        [10.0.0.1/24, 10.0.0.2/24, 10.0.0.3/24, 10.0.0.4/24, 10.0.0.5/24, ...]

        To create a single IP:

        >>> prefix = nb.ipam.prefixes.get(24)
        >>> prefix.available_ips.create()
        10.0.0.1/24


        To create multiple IPs:

        >>> prefix = nb.ipam.prefixes.get(24)
        >>> create = prefix.available_ips.create([{} for i in range(2)])
        >>> create
        [10.0.0.2/24, 10.0.0.3/24]
        """
        return DetailEndpoint(self, "available-ips", custom_return=IpAddresses)

    @property
    def available_prefixes(self):
        """Represents the ``available-prefixes`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing and creating prefixes inside a parent prefix.

        Very similar to :py:meth:`~pynetbox.ipam.Prefixes.available_ips`
        , except that dict (or list of dicts) passed to ``.create()``
        needs to have a ``prefix_length`` key/value specifed.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> prefix = nb.ipam.prefixes.get(3)
        >>> prefix
        10.0.0.0/16
        >>> prefix.available_prefixes.list()
        [10.0.1.0/24, 10.0.2.0/23, 10.0.4.0/22, 10.0.8.0/21, 10.0.16.0/20, 10.0.32.0/19, 10.0.64.0/18, 10.0.128.0/17]


        Creating a single child prefix:

        >>> prefix = nb.ipam.prefixes.get(1)
        >>> prefix
        10.0.0.0/24
        >>> new_prefix = prefix.available_prefixes.create(
        ...     {"prefix_length": 29}
        ... )
        >>> new_prefix
        10.0.0.16/29

        """
        return DetailEndpoint(self, "available-prefixes", custom_return=Prefixes)


class Aggregates(Record):
    def __str__(self):
        return str(self.prefix)


class Vlans(Record):
    def __str__(self):
        return super().__str__() or str(self.vid)


class VlanGroups(Record):
    @property
    def available_vlans(self):
        """Represents the ``available-vlans`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing and creating VLANs inside a VLAN group.

        Available since NetBox 3.2.0.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> vlan_group = nb.ipam.vlan_groups.get(1)
        >>> vlan_group.available_vlans.list()
        [10, 11, 12]

        To create a new VLAN:

        >>> vlan_group.available_vlans.create({"name": "NewVLAN"})
        NewVLAN (10)
        """
        return DetailEndpoint(self, "available-vlans", custom_return=Vlans)
