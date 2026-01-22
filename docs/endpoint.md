# Endpoint

`Endpoint` objects provide CRUD operations for NetBox API endpoints. They are automatically created when you access attributes on [App](api.md#app-class) objects.

## Overview

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Accessing an attribute on an App returns an Endpoint
devices = nb.dcim.devices  # This is an Endpoint instance

# Use Endpoint methods for CRUD operations
all_devices = devices.all()
device = devices.get(1)
filtered = devices.filter(site='headquarters')
new_device = devices.create(name='test', site=1, device_type=1, device_role=1)
```

::: pynetbox.core.endpoint.Endpoint
    handler: python
    options:
        members:
            - all
            - choices
            - count
            - create
            - delete
            - filter
            - get
            - update
        show_source: true
        show_root_heading: true
        heading_level: 2

::: pynetbox.core.endpoint.DetailEndpoint
    handler: python
    options:
        members:
            - create
            - list
        show_source: true
        show_root_heading: true
        heading_level: 2
