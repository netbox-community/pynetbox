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
from pynetbox.core.response import Record, JsonField
from pynetbox.core.endpoint import RODetailEndpoint
from pynetbox.models.ipam import IpAddresses
from pynetbox.models.circuits import Circuits


class DeviceTypes(Record):
    def __str__(self):
        return self.model


class Devices(Record):
    """Devices Object

        Represents a device response from netbox.

        Attributes:
            primary_ip, ip4, ip6 (list): Tells __init__ in Record() to
                take the `primary_ip` field's value from the API
                response and return an initialized list of IpAddress
                objects
            device_type (obj): Tells __init__ in Record() to take the
                `device_type` field's value from the API response and
                return an initialized DeviceType object
    """

    has_details = True
    device_type = DeviceTypes
    primary_ip = IpAddresses
    primary_ip4 = IpAddresses
    primary_ip6 = IpAddresses
    local_context_data = JsonField
    config_context = JsonField

    @property
    def napalm(self):
        """ Represents the ``napalm`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing response from the napalm endpoint.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> device = nb.ipam.devices.get(123)
        >>> device.napalm.list(method='get_facts')
        {"get_facts": {"interface_list": ["ge-0/0/0"]}}

        """
        return RODetailEndpoint(self, "napalm")


class InterfaceConnections(Record):
    def __str__(self):
        return self.interface_a.name


class InterfaceConnection(Record):
    def __str__(self):
        return self.interface.name


class ConnectedEndpoint(Record):
    device = Devices


class Interfaces(Record):
    interface_connection = InterfaceConnection
    connected_endpoint = ConnectedEndpoint


class RackReservations(Record):
    def __str__(self):
        return self.description


class VirtualChassis(Record):
    def __str__(self):
        return self.master.display_name


class RUs(Record):
    device = Devices


class Racks(Record):
    @property
    def units(self):
        """ Represents the ``units`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing response from the units endpoint.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> rack = nb.dcim.racks.get(123)
        >>> rack.units.list()
        {"get_facts": {"interface_list": ["ge-0/0/0"]}}

        """
        return RODetailEndpoint(self, "units", custom_return=RUs)

    @property
    def elevation(self):
        """ Represents the ``elevation`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        viewing response from the elevation endpoint updated in
        Netbox version 2.8.

        :returns: :py:class:`.DetailEndpoint`

        :Examples:

        >>> rack = nb.dcim.racks.get(123)
        >>> rack.elevation.list()
        {"get_facts": {"interface_list": ["ge-0/0/0"]}}

        """
        return RODetailEndpoint(self, "elevation", custom_return=RUs)


class Termination(Record):
    def __str__(self):
        # hacky check to see if we're a circuit termination to
        # avoid another call to NetBox because of a non-existent attr
        # in self.name
        if "circuit" in str(self.url):
            return self.circuit.cid

        return self.name

    device = Devices
    circuit = Circuits


class Cables(Record):
    def __str__(self):
        return "{} <> {}".format(self.termination_a, self.termination_b)

    termination_a = Termination
    termination_b = Termination
