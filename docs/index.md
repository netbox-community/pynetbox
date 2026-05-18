# pynetbox Documentation

Python API client library for [NetBox](https://github.com/netbox-community/netbox).

## Overview

pynetbox is a Python client library that provides a simple, Pythonic interface to NetBox's REST API. It handles authentication, pagination, and serialization, allowing you to read and write NetBox data without dealing with raw HTTP requests.

## Features

- **Intuitive API**: NetBox apps and endpoints are exposed as Python attributes (`nb.dcim.devices`).
- **Full CRUD support**: Create, read, update, and delete NetBox objects.
- **Threading**: Optional parallel page fetching for large result sets.
- **Filter validation**: Optional strict validation of filter parameters against NetBox's OpenAPI specification.
- **Custom sessions**: Drop in your own `requests.Session` for custom SSL, timeouts, and retries.
- **Branching plugin support**: Context manager for the NetBox branching plugin.
- **Comprehensive coverage**: Supports every built-in NetBox app (DCIM, IPAM, Circuits, Virtualization, Tenancy, Extras, Users, Wireless, VPN, Core) plus plugin endpoints.

## NetBox Version Compatibility

!!! warning "Version Requirements"
    pynetbox 6.7 and later support only NetBox 3.3 and above.

Each pynetbox version has been tested against the corresponding NetBox versions:

| pynetbox Version |   NetBox Version   |
|:----------------:|:------------------:|
|      7.7.0       | 4.3, 4.4, 4.5, 4.6 |
|      7.6.1       |        4.5         |
|      7.6.0       |        4.5         |
|      7.5.0       | 4.1, 4.2, 4.3, 4.4 |
|      7.4.1       |       4.0.6        |
|      7.4.0       |        4.0         |
|      7.3.x       |        3.7         |
|      7.2.0       |        3.6         |
|      7.1.0       |        3.5         |
|      7.0.x       |      3.3, 3.4      |

## Quick Example

```python
import pynetbox

# Initialize the API connection
nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)

# Query all devices
for device in nb.dcim.devices.all():
    print(device.name)

# Filter devices
leaf_switches = nb.dcim.devices.filter(role='leaf-switch')

# Get a specific device
device = nb.dcim.devices.get(name='spine1')

# Create a new device
new_device = nb.dcim.devices.create(
    name='new-device',
    device_type=1,
    site=1,
    role=1,
)

# Update a device
device.serial = 'ABC123'
device.save()
```

## Getting Help

- **GitHub Issues**: Report bugs or request features at [github.com/netbox-community/pynetbox/issues](https://github.com/netbox-community/pynetbox/issues).
- **GitHub Discussions**: General questions and discussion at [github.com/netbox-community/pynetbox/discussions](https://github.com/netbox-community/pynetbox/discussions).
- **Source Code**: [github.com/netbox-community/pynetbox](https://github.com/netbox-community/pynetbox).
