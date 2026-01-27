# API Core Classes

This page documents the core classes that form pyNetBox's API structure.

## Overview

PyNetBox uses a layered architecture to interact with NetBox:

1. **Api** - The main entry point that creates connections to NetBox
2. **App** - Represents NetBox applications (dcim, ipam, circuits, etc.)
3. **Endpoint** - Provides CRUD operations for specific API endpoints

```python
import pynetbox

# Create API connection (Api class)
nb = pynetbox.api('http://localhost:8000', token='your-token')

# Access an app (App class)
nb.dcim  # Returns an App instance

# Access an endpoint (Endpoint class)
nb.dcim.devices  # Returns an Endpoint instance

# Use endpoint methods
devices = nb.dcim.devices.all()
```

## Api Class

The `Api` class is the main entry point for interacting with NetBox. It manages the HTTP session, authentication, and provides access to NetBox applications.

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
        heading_level: 3

## App Class

The `App` class represents a NetBox application (such as dcim, ipam, circuits). When you access an attribute on the `Api` object, it returns an `App` instance. Accessing attributes on an `App` returns `Endpoint` objects.

::: pynetbox.core.app.App
    handler: python
    options:
        members:
            - config
        show_source: true
        show_root_heading: true
        heading_level: 3

## Relationship to Endpoints

When you access an attribute on an `App` object, it returns an [Endpoint](endpoint.md) instance:

```python
# nb.dcim is an App instance
# nb.dcim.devices is an Endpoint instance
devices_endpoint = nb.dcim.devices

# Endpoint provides CRUD methods
all_devices = devices_endpoint.all()
device = devices_endpoint.get(1)
new_device = devices_endpoint.create(name='test', site=1, device_type=1, device_role=1)
```

See the [Endpoint documentation](endpoint.md) for details on available methods.
