# Getting Started

This guide will walk you through the basics of using pyNetBox to interact with NetBox.

## Basic Connection

First, import pynetbox and create an API connection:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
```

### Connection Parameters

The `api()` method accepts several parameters:

- **url** (required): The base URL of your NetBox instance
- **token** (optional): API authentication token (required for write operations)
- **threading** (optional): Enable multithreaded requests (default: `False`)
- **strict_filters** (optional): Enable filter validation (default: `False`)

```python
nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token-here',
    threading=True,
    strict_filters=True
)
```

## Understanding the API Structure

PyNetBox mirrors NetBox's app structure. NetBox apps become attributes of the API object:

```python
nb.dcim      # Data Center Infrastructure Management
nb.ipam      # IP Address Management
nb.circuits  # Circuit management
nb.virtualization  # Virtual machines and clusters
nb.tenancy   # Tenants and contacts
nb.extras    # Tags, custom fields, etc.
nb.users     # Users and permissions
nb.wireless  # Wireless LANs and links
nb.core      # Core objects (data sources, jobs)
nb.vpn       # VPN tunnels and terminations
```

Each app has endpoints that correspond to NetBox's API endpoints:

```python
nb.dcim.devices
nb.dcim.sites
nb.dcim.racks
nb.ipam.ip_addresses
nb.ipam.prefixes
# ... and so on
```

## Querying Data

### Getting All Objects

Use `.all()` to retrieve all objects from an endpoint:

```python
# Get all devices
devices = nb.dcim.devices.all()
for device in devices:
    print(device.name)
```

!!! warning "Generator Objects"
    The `.all()` and `.filter()` methods return generators that can only be iterated once.
    To iterate multiple times, wrap the result in a `list()`:

    ```python
    devices = list(nb.dcim.devices.all())
    ```

### Filtering Objects

Use `.filter()` to query specific objects:

```python
# Get all devices with a specific role
leaf_switches = nb.dcim.devices.filter(role='leaf-switch')

# Multiple filters
devices = nb.dcim.devices.filter(
    site='headquarters',
    status='active',
    role='access-switch'
)

# Filter by custom fields
devices = nb.dcim.devices.filter(cf_environment='production')
```

### Getting a Single Object

Use `.get()` to retrieve a specific object:

```python
# Get by ID
device = nb.dcim.devices.get(1)

# Get by name
device = nb.dcim.devices.get(name='spine1')

# Get returns None if not found
device = nb.dcim.devices.get(name='nonexistent')
if device is None:
    print("Device not found")
```

## Working with Objects

### Accessing Attributes

Objects return attributes as properties:

```python
device = nb.dcim.devices.get(1)
print(device.name)
print(device.serial)
print(device.device_type)
print(device.site.name)  # Nested objects
```

### Checking Available Attributes

```python
device = nb.dcim.devices.get(1)

# Convert to dict to see all attributes
print(dict(device))

# Or access the raw data
print(device.serialize())
```

## Creating Objects

Use `.create()` to create new objects:

```python
# Create a new site
new_site = nb.dcim.sites.create(
    name='new-datacenter',
    slug='new-datacenter',
    status='planned'
)

# Create a device
new_device = nb.dcim.devices.create(
    name='new-switch',
    device_type=1,  # Can use ID
    site=new_site.id,  # Or reference the created object
    device_role=5
)

# Create with nested data
new_ip = nb.ipam.ip_addresses.create(
    address='10.0.0.1/24',
    status='active',
    assigned_object_type='dcim.interface',
    assigned_object_id=123
)
```

## Updating Objects

There are two ways to update objects:

### Method 1: Update and Save

```python
device = nb.dcim.devices.get(1)
device.serial = 'ABC123'
device.asset_tag = 'ASSET001'
device.save()
```

### Method 2: Using Update

```python
device = nb.dcim.devices.get(1)
device.update({
    'serial': 'ABC123',
    'asset_tag': 'ASSET001'
})
```

## Deleting Objects

Use `.delete()` to remove objects:

```python
device = nb.dcim.devices.get(1)
device.delete()

# Or delete directly by ID
nb.dcim.devices.delete(1)
```

## Working with Choices

Get available choices for choice fields:

```python
# Get all status choices for devices
statuses = nb.dcim.devices.choices()
print(statuses['status'])

# Get choices for a specific field
interface_types = nb.dcim.interfaces.choices()
print(interface_types['type'])
```

## Pagination

NetBox paginates results by default. PyNetBox handles pagination automatically:

```python
# This will automatically fetch all pages
devices = nb.dcim.devices.all()

# You can also limit results
devices = nb.dcim.devices.filter(limit=10)
```

## Error Handling

```python
from pynetbox.core.query import RequestError, ContentError

try:
    device = nb.dcim.devices.create(
        name='test-device',
        device_type=1,
        site=1,
        device_role=1
    )
except RequestError as e:
    print(f"Request failed: {e}")
except ContentError as e:
    print(f"Content error: {e}")
```

## Next Steps

- Review the [API Reference](api.md) for detailed documentation on core classes
- Learn about [Threading](advanced.md#threading) for faster queries
- Explore [Filter Validation](advanced.md#filter-validation) for safer queries
- Review special methods documentation:
  - [DCIM Special Methods](dcim.md)
  - [IPAM Special Methods](ipam.md)
  - [Virtualization Special Methods](virtualization.md)
- Check out [Advanced Topics](advanced.md) for custom sessions and branching
- Refer to [NetBox API Documentation](https://demo.netbox.dev/api/docs/) for standard CRUD operations
