# Quick Start

This guide walks through the basics of using pynetbox to interact with NetBox.

## Basic Connection

Import `pynetbox` and create an API connection:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
```

### Connection Parameters

`pynetbox.api()` accepts the following parameters:

- **`url`** (required): Base URL of your NetBox instance, including scheme (`http://` or `https://`).
- **`token`** (optional): API authentication token. Required for write operations and for endpoints that are not public.
- **`threading`** (optional, default `False`): Enable multithreaded page fetching for `.all()` and `.filter()`. See [Threading](advanced.md#threading).
- **`strict_filters`** (optional, default `False`): Validate filter parameters against NetBox's OpenAPI specification. See [Filter Validation](advanced.md#filter-validation).

```python
nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token-here',
    threading=True,
    strict_filters=True,
)
```

## API Structure

pynetbox mirrors NetBox's app structure. Each NetBox app is exposed as an attribute of the API object:

```python
nb.circuits         # Circuit management
nb.core             # Core objects (data sources, jobs, object changes)
nb.dcim             # Data Center Infrastructure Management
nb.extras           # Tags, custom fields, webhooks, etc.
nb.ipam             # IP Address Management
nb.tenancy          # Tenants and contacts
nb.users            # Users and permissions
nb.virtualization   # Virtual machines and clusters
nb.vpn              # VPN tunnels and terminations
nb.wireless         # Wireless LANs and links
```

Each app exposes endpoints that map to NetBox API endpoints. Dashes in endpoint names are converted to underscores:

```python
nb.dcim.devices
nb.dcim.sites
nb.dcim.racks
nb.ipam.ip_addresses   # /api/ipam/ip-addresses/
nb.ipam.prefixes
```

### Plugin Endpoints

Endpoints provided by NetBox plugins are accessible under the `plugins` namespace. As with built-in endpoints, dashes in plugin or endpoint names are converted to underscores:

```python
# /api/plugins/my-plugin/objects/
nb.plugins.my_plugin.objects.all()
```

## Querying Data

### Getting All Objects

Use `.all()` to retrieve every object from an endpoint:

```python
for device in nb.dcim.devices.all():
    print(device.name)
```

!!! warning "RecordSet is a one-shot iterator"
    `.all()` and `.filter()` return a `RecordSet`, which can only be iterated once. To iterate the results multiple times, materialize them with `list()`:

    ```python
    devices = list(nb.dcim.devices.all())
    ```

### Filtering Objects

Use `.filter()` to query objects matching one or more criteria. Keyword arguments correspond to filter parameters supported by the NetBox endpoint:

```python
# All devices with a specific role
leaf_switches = nb.dcim.devices.filter(role='leaf-switch')

# Multiple filters (AND)
devices = nb.dcim.devices.filter(
    site='headquarters',
    status='active',
    role='access-switch',
)

# Filter on a custom field
devices = nb.dcim.devices.filter(cf_environment='production')

# Freeform search (passed as ?q=...)
results = nb.dcim.devices.filter('rack1')
```

!!! note "Invalid filters do not raise an error by default"
    NetBox silently ignores unrecognized filter parameters, which means a typo can quietly return the entire table. Enable [strict filter validation](advanced.md#filter-validation) to catch these errors early.

### Getting a Single Object

Use `.get()` to retrieve a single object. It returns `None` if no match is found and raises `ValueError` if more than one record matches:

```python
# By ID
device = nb.dcim.devices.get(1)

# By a unique field
device = nb.dcim.devices.get(name='spine1')

# Combining filters when a single field is not unique
location = nb.dcim.locations.get(site='site-1', name='Row 1')

# get() returns None if no match is found
device = nb.dcim.devices.get(name='nonexistent')
if device is None:
    print("Device not found")
```

### Counting Objects

Use `.count()` to retrieve only the count of matching objects without fetching them:

```python
total = nb.dcim.devices.count()
active = nb.dcim.devices.count(status='active')
```

## Working with Records

### Accessing Attributes

API fields are exposed as attributes on `Record` objects:

```python
device = nb.dcim.devices.get(1)
print(device.name)
print(device.serial)
print(device.device_type.model)   # Nested object
print(device.site.name)
```

### Inspecting Available Attributes

```python
device = nb.dcim.devices.get(1)

# As a dict
print(dict(device))

# Or get the data structure ready for an API payload
print(device.serialize())
```

## Creating Objects

Use `.create()` to create new objects. Pass field values as keyword arguments:

```python
# Create a site
new_site = nb.dcim.sites.create(
    name='new-datacenter',
    slug='new-datacenter',
    status='planned',
)

# Create a device (NetBox 3.6+ uses `role`; pre-3.6 used `device_role`)
new_device = nb.dcim.devices.create(
    name='new-switch',
    device_type=1,
    site=new_site.id,
    role=5,
)

# Create an IP address with assignment to an interface
new_ip = nb.ipam.ip_addresses.create(
    address='10.0.0.1/24',
    status='active',
    assigned_object_type='dcim.interface',
    assigned_object_id=123,
)
```

To create multiple objects in a single request, pass a list of dicts:

```python
nb.dcim.sites.create([
    {'name': 'site-1', 'slug': 'site-1'},
    {'name': 'site-2', 'slug': 'site-2'},
])
```

## Updating Objects

There are two ways to update a single object.

### Modify attributes and `save()`

```python
device = nb.dcim.devices.get(1)
device.serial = 'ABC123'
device.asset_tag = 'ASSET001'
device.save()
```

`save()` sends a PATCH containing only the fields that have changed and returns `True` if the request succeeded.

### Pass a dict to `update()`

```python
device = nb.dcim.devices.get(1)
device.update({
    'serial': 'ABC123',
    'asset_tag': 'ASSET001',
})
```

### Bulk Updates

To update multiple records in a single request, call `.update()` on the endpoint with a list of records or dicts. Each dict must include an `id`:

```python
devices = nb.dcim.devices.filter(site='test1')
for device in devices:
    device.status = 'active'
nb.dcim.devices.update(devices)
```

`RecordSet` also supports a chainable form:

```python
nb.dcim.devices.filter(site_id=1).update(status='active')
```

## Deleting Objects

Use `.delete()` to remove an object:

```python
device = nb.dcim.devices.get(1)
device.delete()
```

To delete multiple objects in a single request, pass a list (or `RecordSet`) of records or IDs to the endpoint's `.delete()`:

```python
nb.dcim.devices.delete([1, 2, 3])

# Or, delete every record matching a filter:
nb.dcim.devices.filter(status='offline').delete()
```

## Working with Choices

Use `.choices()` to retrieve the valid values for each choice field on an endpoint. The return value is a dict keyed by field name, with each value being a list of `{value, label}` entries:

```python
choices = nb.dcim.devices.choices()
for choice in choices['status']:
    print(choice['value'], choice['label'])
# active     Active
# planned    Planned
# staged     Staged
# ...
```

## Pagination

NetBox paginates list responses, but pynetbox fetches subsequent pages automatically as you iterate the result set. You can override the page size with `limit`:

```python
# Fetch 100 records per page (instead of the server default)
devices = nb.dcim.devices.filter(limit=100)

# Start at a specific offset (requires a positive limit)
devices = nb.dcim.devices.filter(limit=100, offset=200)
```

## Error Handling

pynetbox raises specific exceptions for different failure modes:

```python
import pynetbox

try:
    nb.dcim.devices.create(
        name='test-device',
        device_type=1,
        site=1,
        role=1,
    )
except pynetbox.RequestError as e:
    # HTTP error from NetBox (4xx/5xx)
    print(f"Request failed: {e.error}")
except pynetbox.AllocationError as e:
    # No room left in an available-ips / available-prefixes pool
    print(f"Allocation failed: {e}")
except pynetbox.ContentError as e:
    # Server returned a non-JSON response (usually a misconfigured URL)
    print(f"Content error: {e}")
except pynetbox.ParameterValidationError as e:
    # strict_filters=True and a filter parameter is invalid
    print(f"Invalid filter: {e}")
```

## Next Steps

- [API Reference](api.md) — detailed documentation of the core classes.
- [Advanced Topics](advanced.md) — threading, filter validation, custom sessions, file uploads.
- Endpoint-specific helpers:
    - [DCIM](dcim.md)
    - [IPAM](ipam.md)
    - [Circuits](circuits.md)
    - [Virtualization](virtualization.md)
- [NetBox REST API documentation](https://demo.netbox.dev/api/docs/) — the canonical reference for fields and filters.
