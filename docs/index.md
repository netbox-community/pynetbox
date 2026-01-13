# PyNetBox Documentation

Python API client library for [NetBox](https://github.com/netbox-community/netbox).

## Overview

PyNetBox is a Python client library that provides a simple and intuitive interface to interact with the NetBox REST API. It abstracts the complexity of making HTTP requests and provides a Pythonic way to work with NetBox data.

## Features

- **Intuitive API**: Access NetBox endpoints through simple Python attributes
- **Full CRUD Support**: Create, read, update, and delete NetBox objects
- **Threading Support**: Parallel requests for improved performance on large queries
- **Filter Validation**: Optional strict validation of filters against NetBox's OpenAPI spec
- **Custom Sessions**: Support for custom HTTP sessions with SSL, timeouts, and retries
- **Branch Support**: Context manager for NetBox branching plugin
- **Comprehensive Coverage**: Support for all NetBox apps (DCIM, IPAM, Circuits, Virtualization, etc.)

## NetBox Version Compatibility

!!! warning "Version Requirements"
    Version 6.7 and later of pyNetBox only supports NetBox 3.3 and above.

Each pyNetBox version has been tested with its corresponding NetBox version:

| NetBox Version | PyNetBox Version |
|:--------------:|:----------------:|
|      4.5       |     7.6.0        |
|      4.4       |     7.5.0        |
|      4.3       |     7.5.0        |
|      4.2       |     7.5.0        |
|      4.1       |     7.5.0        |
|      4.0.6     |     7.4.1        |
|      4.0.0     |     7.3.4        |
|      3.7       |     7.3.0        |
|      3.6       |     7.2.0        |
|      3.5       |     7.1.0        |
|      3.3       |     7.0.0        |

## Quick Example

```python
import pynetbox

# Initialize the API connection
nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)

# Query all devices
devices = nb.dcim.devices.all()
for device in devices:
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
    device_role=1
)

# Update a device
device.serial = 'ABC123'
device.save()
```

## Getting Help

- **GitHub Issues**: Report bugs or request features at [github.com/netbox-community/pynetbox/issues](https://github.com/netbox-community/pynetbox/issues)
- **Documentation**: Full API reference and guides available in this documentation
- **Source Code**: Available at [github.com/netbox-community/pynetbox](https://github.com/netbox-community/pynetbox)

## API Reference

::: pynetbox.core.api.Api
    handler: python
    options:
        members:
            - __init__
            - create_token
            - openapi
            - status
            - version
            - activate_branch
        show_source: true
        show_root_heading: true

## App Reference

::: pynetbox.core.app.App
    handler: python
    options:
        members:
            - config
        show_source: true
        show_root_heading: true
