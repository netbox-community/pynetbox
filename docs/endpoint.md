# Endpoint

`Endpoint` objects provide CRUD operations for NetBox API endpoints. They are created automatically when you access an attribute on an [`App`](api.md#app) instance.

## Overview

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Accessing an attribute on an App returns an Endpoint
devices = nb.dcim.devices  # Endpoint

# Endpoint methods perform CRUD operations
all_devices = devices.all()
device = devices.get(1)
filtered = devices.filter(site='headquarters')
new_device = devices.create(name='test', site=1, device_type=1, role=1)
```

## Endpoint Class

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
        heading_level: 3

## DetailEndpoint Class

`DetailEndpoint` represents a detail route on an existing record (e.g. `/api/ipam/prefixes/{id}/available-ips/`). It is returned by model-specific properties such as `Prefixes.available_ips`, not constructed directly.

::: pynetbox.core.endpoint.DetailEndpoint
    handler: python
    options:
        members:
            - create
            - list
        show_source: true
        show_root_heading: true
        heading_level: 3

## ROMultiFormatDetailEndpoint Class

A read-only detail endpoint that supports multiple response formats. Used for endpoints (such as rack elevation) that can return either structured JSON or raw content like SVG.

::: pynetbox.core.endpoint.ROMultiFormatDetailEndpoint
    handler: python
    options:
        members:
            - list
        show_source: true
        show_root_heading: true
        heading_level: 3
