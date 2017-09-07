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
from pynetbox.lib.response import Record
from pynetbox.ipam import IpAddresses


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


class InterfaceConnections(Record):

    def __str__(self):
        return self.interface_a.name


class InterfaceConnection(Record):

    def __str__(self):
        return self.interface.name


class Interfaces(Record):
    interface_connection = InterfaceConnection


class RackReservations(Record):

    def __str__(self):
        return self.description
