# Core Classes

This page documents the core classes that form pynetbox's API surface.

## Overview

pynetbox uses a layered architecture, with each layer wrapping the one below:

1. **`Api`** — main entry point; manages the HTTP session, authentication token, and global flags.
2. **`App`** — represents a NetBox application (e.g. `dcim`, `ipam`); attribute access returns endpoints.
3. **`Endpoint`** — represents an individual NetBox API endpoint and exposes CRUD methods.

```python
import pynetbox

# Create an API connection (Api)
nb = pynetbox.api('http://localhost:8000', token='your-token')

# Access an app (App)
nb.dcim

# Access an endpoint (Endpoint)
nb.dcim.devices

# Call an endpoint method (returns Record / RecordSet)
devices = nb.dcim.devices.all()
```

## Api

The `Api` class is the main entry point. It manages the underlying `requests.Session`, holds the authentication token, and provides access to NetBox applications.

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

## App

The `App` class represents a NetBox application (such as `dcim`, `ipam`, or `circuits`). Accessing an attribute on the `Api` instance returns an `App`; accessing an attribute on an `App` returns an `Endpoint`.

::: pynetbox.core.app.App
    handler: python
    options:
        members:
            - config
            - endpoint
        show_source: true
        show_root_heading: true
        heading_level: 3

## PluginsApp

The `PluginsApp` class exposes plugin endpoints under `nb.plugins`. Plugin and endpoint names containing dashes are accessed using underscores (e.g. `/api/plugins/my-plugin/objects/` becomes `nb.plugins.my_plugin.objects`).

::: pynetbox.core.app.PluginsApp
    handler: python
    options:
        members:
            - installed_plugins
        show_source: true
        show_root_heading: true
        heading_level: 3

## Relationship to Endpoints

Attribute access on an `App` returns an [`Endpoint`](endpoint.md) instance:

```python
# nb.dcim is an App
# nb.dcim.devices is an Endpoint
devices_endpoint = nb.dcim.devices

# Endpoint provides CRUD methods
all_devices = devices_endpoint.all()
device = devices_endpoint.get(1)
new_device = devices_endpoint.create(name='test', site=1, device_type=1, role=1)
```

See the [Endpoint reference](endpoint.md) for the full method list.
