# DCIM

This page documents the special methods available on DCIM models. Standard CRUD operations follow the patterns described in [Quick Start](getting-started.md) and the [Endpoint reference](endpoint.md).

!!! note "Standard API Operations"
    The standard endpoint methods (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for the available fields and filters on each endpoint.

## Devices

### NAPALM Integration

The `napalm` property exposes the `/napalm/` detail route on a device, providing live data fetched from the device through NAPALM. This requires NAPALM to be configured on the NetBox server.

::: pynetbox.models.dcim.Devices.napalm
    handler: python
    options:
        show_source: true

**Example:**

```python
device = nb.dcim.devices.get(name='router1')

# Device facts
facts = device.napalm.list(method='get_facts')

# Interfaces
interfaces = device.napalm.list(method='get_interfaces')

# ARP table
arp = device.napalm.list(method='get_arp_table')
```

### Config Rendering

The `render_config` property renders a device's configuration from its assigned config template and config contexts.

::: pynetbox.models.dcim.Devices.render_config
    handler: python
    options:
        show_source: true

**Example:**

```python
device = nb.dcim.devices.get(name='switch1')
config = device.render_config.create()
print(config)
```

## Racks

### Rack Units

The `units` property returns information about each rack unit and the device installed in it.

::: pynetbox.models.dcim.Racks.units
    handler: python
    options:
        show_source: true

**Example:**

```python
rack = nb.dcim.racks.get(name='RACK-01')

for unit in rack.units.list():
    if unit.device:
        print(f"U{unit.name}: {unit.device.name}")
    else:
        print(f"U{unit.name}: Empty")
```

### Rack Elevation

The `elevation` property supports both JSON and SVG output. By default it returns a list of rack-unit records; passing `render='svg'` returns a rendered SVG diagram as a string.

::: pynetbox.models.dcim.Racks.elevation
    handler: python
    options:
        show_source: true

**Examples:**

```python
rack = nb.dcim.racks.get(name='RACK-01')

# As JSON (list of RU objects)
elevation_data = rack.elevation.list()

# As an SVG diagram
svg_diagram = rack.elevation.list(render='svg')

with open('rack-elevation.svg', 'w') as f:
    f.write(svg_diagram)
```

## Cable Tracing

Several DCIM models expose a `trace()` method that traces a cable end-to-end, returning each hop of the path.

**Supported models:**

- Interfaces
- ConsolePorts
- ConsoleServerPorts
- PowerPorts
- PowerOutlets
- PowerFeeds

The return value is a flat list arranged as `[a_terminations, cable, b_terminations, a_terminations, cable, b_terminations, ...]`, where each `*_terminations` entry is a list of Record objects and each `cable` entry is either a `Cables` record or `None` for an incomplete path.

**Example:**

```python
interface = nb.dcim.interfaces.get(name='eth0', device='switch1')
trace_result = interface.trace()

for item in trace_result:
    if isinstance(item, list):
        # Terminations
        for term in item:
            print(f"  Termination: {term}")
    else:
        # Cable (or None for an incomplete path)
        if item:
            print(f"  Cable: {item.id} - {item.label}")
        else:
            print("  No cable")

# Console port
console = nb.dcim.console_ports.get(name='Console', device='router1')
console_trace = console.trace()

# Power connection
power_port = nb.dcim.power_ports.get(name='PSU1', device='server1')
power_trace = power_port.trace()
```

## Cable Path Tracing (Pass-Through Ports)

Front ports and rear ports use the `paths()` method instead of `trace()` because a single port can participate in multiple complete cable paths.

**Supported models:**

- FrontPorts
- RearPorts

**Example:**

```python
front_port = nb.dcim.front_ports.get(name='FrontPort1', device='patch-panel-1')

for path_info in front_port.paths():
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Rear ports work the same way
rear_port = nb.dcim.rear_ports.get(name='RearPort1', device='patch-panel-1')
rear_paths = rear_port.paths()

if rear_paths:
    first_path = rear_paths[0]
    if first_path['origin']:
        print(f"Cable path starts at: {first_path['origin']}")
    if first_path['destination']:
        print(f"Cable path ends at: {first_path['destination']}")
```

**Path Structure:**

`paths()` returns a list of dictionaries, one per complete cable path. Each dictionary contains:

- `origin`: The starting endpoint of the path (`Record` or `None` if unconnected).
- `destination`: The ending endpoint of the path (`Record` or `None` if unconnected).
- `path`: A list of path segments. Each segment is a list of `Record` objects representing the components in that segment (cables, terminations, etc.).
