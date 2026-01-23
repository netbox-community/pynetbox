# DCIM

This page documents special methods available for DCIM models in pyNetBox.

!!! note "Standard API Operations"
    Standard CRUD operations (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API patterns. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for details on available endpoints and filters.

## Devices

### NAPALM Integration

The `napalm` property provides access to NAPALM device data.

::: pynetbox.models.dcim.Devices.napalm
    handler: python
    options:
        show_source: true

**Example:**
```python
device = nb.dcim.devices.get(name='router1')

# Get device facts
facts = device.napalm.list(method='get_facts')
print(facts)

# Get interfaces
interfaces = device.napalm.list(method='get_interfaces')

# Get ARP table
arp = device.napalm.list(method='get_arp_table')
```

### Config Rendering

The `render_config` property renders device configuration based on config contexts and templates.

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

The `units` property provides access to rack unit information.

::: pynetbox.models.dcim.Racks.units
    handler: python
    options:
        show_source: true

**Example:**
```python
rack = nb.dcim.racks.get(name='RACK-01')
units = rack.units.list()

for unit in units:
    if unit.device:
        print(f"U{unit.name}: {unit.device.name}")
    else:
        print(f"U{unit.name}: Empty")
```

### Rack Elevation

The `elevation` property supports both JSON and SVG output for rack elevation diagrams.

::: pynetbox.models.dcim.Racks.elevation
    handler: python
    options:
        show_source: true

**Examples:**
```python
rack = nb.dcim.racks.get(name='RACK-01')

# Get elevation as JSON (returns list of RU objects)
elevation_data = rack.elevation.list()

# Get elevation as SVG diagram
svg_diagram = rack.elevation.list(render='svg')

# Save SVG to file
with open('rack-elevation.svg', 'w') as f:
    f.write(svg_diagram)
```

## Cable Tracing

Several DCIM models support cable path tracing through the `trace()` method.

**Models with cable tracing:**
- Interfaces
- ConsolePorts
- ConsoleServerPorts
- PowerPorts
- PowerOutlets
- PowerFeeds

**Example:**
```python
# Trace a network interface
interface = nb.dcim.interfaces.get(name='eth0', device='switch1')
trace_result = interface.trace()

# The trace returns a list of [terminations, cable, terminations]
for item in trace_result:
    if isinstance(item, list):
        # Terminations
        for term in item:
            print(f"  Termination: {term}")
    else:
        # Cable or None
        if item:
            print(f"  Cable: {item.id} - {item.label}")
        else:
            print("  No cable")

# Trace console port
console = nb.dcim.console_ports.get(name='Console', device='router1')
console_trace = console.trace()

# Trace power connections
power_port = nb.dcim.power_ports.get(name='PSU1', device='server1')
power_trace = power_port.trace()
```

## Cable Path Tracing (Pass-Through Ports)

Front ports and rear ports use the `paths()` method instead of `trace()`. The `paths()` method returns all cable paths that traverse through the port, from origin to destination.

**Models with cable path tracing:**
- FrontPorts
- RearPorts

**Example:**
```python
# Get paths through a front port
front_port = nb.dcim.front_ports.get(name='FrontPort1', device='patch-panel-1')
paths = front_port.paths()

# Each path contains origin, destination, and path segments
for path_info in paths:
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Get paths through a rear port
rear_port = nb.dcim.rear_ports.get(name='RearPort1', device='patch-panel-1')
rear_paths = rear_port.paths()

# Access the complete path from origin to destination
if rear_paths:
    first_path = rear_paths[0]
    if first_path['origin']:
        print(f"Cable path starts at: {first_path['origin']}")
    if first_path['destination']:
        print(f"Cable path ends at: {first_path['destination']}")
```

**Path Structure:**

The `paths()` method returns a list of dictionaries, where each dictionary represents a complete cable path:

- `origin`: The starting endpoint of the path (Record object or None if unconnected)
- `destination`: The ending endpoint of the path (Record object or None if unconnected)
- `path`: A list of path segments, where each segment is a list of Record objects representing the components in that segment (cables, terminations, etc.)
