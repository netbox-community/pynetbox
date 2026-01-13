# DCIM (Data Center Infrastructure Management)

The DCIM module provides specialized models for working with data center infrastructure in NetBox.

## Overview

The DCIM app includes models with enhanced functionality beyond the standard Record class:

- **Devices**: Device objects with NAPALM integration and config rendering
- **Racks**: Rack objects with unit and elevation endpoints
- **Traceable Records**: Cable path tracing for physical connections
- **Device Types**: Device model information
- **Virtual Chassis**: Stacked switch configurations

## Devices

The `Devices` model provides special methods for device configuration and NAPALM integration.

::: pynetbox.models.dcim.Devices
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Basic Device Operations

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get a device
device = nb.dcim.devices.get(name='spine1')

# Access device attributes
print(device.name)
print(device.device_type.model)
print(device.primary_ip4.address if device.primary_ip4 else "No IP")
print(device.site.name)

# Update device
device.serial = 'SN123456'
device.save()
```

#### NAPALM Integration

```python
# Get device facts via NAPALM
device = nb.dcim.devices.get(name='router1')
facts = device.napalm.list(method='get_facts')
print(facts)
# {"get_facts": {"hostname": "router1", "vendor": "Cisco", ...}}

# Get interfaces
interfaces = device.napalm.list(method='get_interfaces')

# Get ARP table
arp = device.napalm.list(method='get_arp_table')
```

#### Config Rendering

```python
# Render device configuration
device = nb.dcim.devices.get(name='switch1')
config = device.render_config.create()
print(config)
```

#### Working with Config Context

```python
# Access config context (read-only)
device = nb.dcim.devices.get(name='switch1')
print(device.config_context)

# Access local context data (editable)
print(device.local_context_data)

# Update local context data
device.local_context_data = {
    'ntp_servers': ['10.0.0.1', '10.0.0.2'],
    'syslog_servers': ['10.0.0.3']
}
device.save()
```

## Racks

The `Racks` model provides methods for viewing rack units and elevation diagrams.

::: pynetbox.models.dcim.Racks
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Working with Rack Units

```python
# Get a rack
rack = nb.dcim.racks.get(name='RACK-01')

# Get rack unit information
units = rack.units.list()
for unit in units:
    print(f"Unit {unit.name}: {unit.device.name if unit.device else 'Empty'}")

# Check specific unit
unit_42 = rack.units.list(unit=42)
```

#### Elevation Diagrams

```python
# Get elevation as JSON (returns list of RU objects)
rack = nb.dcim.racks.get(name='RACK-01')
elevation_data = rack.elevation.list()

# Get elevation as SVG diagram
svg_diagram = rack.elevation.list(render='svg')

# Save SVG to file
with open('rack_elevation.svg', 'w') as f:
    f.write(svg_diagram)
```

## Cable Tracing

Several DCIM models support cable tracing through the `TraceableRecord` base class.

### Traceable Interfaces

The following models support the `.trace()` method:

- **Interfaces**: Device network interfaces
- **ConsolePorts**: Console ports on devices
- **ConsoleServerPorts**: Console server ports
- **PowerPorts**: Device power connections
- **PowerOutlets**: PDU power outlets
- **PowerFeeds**: Rack power feeds
- **FrontPorts**: Front panel ports
- **RearPorts**: Rear panel ports

### Cable Trace Examples

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

# Trace a console port
console = nb.dcim.console_ports.get(name='Console', device='router1')
console_trace = console.trace()

# Trace power connections
power_port = nb.dcim.power_ports.get(name='PSU1', device='server1')
power_trace = power_port.trace()
```

## Device Types

::: pynetbox.models.dcim.DeviceTypes
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get a device type
device_type = nb.dcim.device_types.get(model='C9300-48P')
print(device_type.model)
print(device_type.manufacturer.name)
print(f"U Height: {device_type.u_height}")

# List all device types from a manufacturer
cisco_types = nb.dcim.device_types.filter(manufacturer='cisco')
for dt in cisco_types:
    print(f"{dt.model} - {dt.u_height}U")
```

## Interfaces

::: pynetbox.models.dcim.Interfaces
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get device interfaces
device = nb.dcim.devices.get(name='switch1')
interfaces = nb.dcim.interfaces.filter(device_id=device.id)

for interface in interfaces:
    print(f"{interface.name}: {interface.type}")
    if interface.connected_endpoints:
        print(f"  Connected to: {interface.connected_endpoints}")

# Create a new interface
new_interface = nb.dcim.interfaces.create(
    device=device.id,
    name='Ethernet1/1',
    type='1000base-t',
    enabled=True
)

# Update interface
interface = nb.dcim.interfaces.get(name='eth0', device='switch1')
interface.description = 'Uplink to Core'
interface.enabled = True
interface.save()
```

## Cables

::: pynetbox.models.dcim.Cables
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Create a cable between two interfaces
cable = nb.dcim.cables.create(
    a_terminations=[
        {
            'object_type': 'dcim.interface',
            'object_id': 123
        }
    ],
    b_terminations=[
        {
            'object_type': 'dcim.interface',
            'object_id': 456
        }
    ],
    type='cat6',
    status='connected',
    label='CABLE-001'
)

# Get cable information
cable = nb.dcim.cables.get(1)
print(cable)  # Shows "Interface A <> Interface B"

# Cable with multiple terminations
print(f"A-side: {cable.a_terminations}")
print(f"B-side: {cable.b_terminations}")
```

## Virtual Chassis

::: pynetbox.models.dcim.VirtualChassis
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get a virtual chassis
vc = nb.dcim.virtual_chassis.get(name='STACK-01')
print(f"Master: {vc.master.name}")
print(f"Members: {len(vc.members)}")

# List all members
for member in vc.members:
    print(f"  {member.name} - Position {member.vc_position}")
```

## Power Management

### Power Feeds

::: pynetbox.models.dcim.PowerFeeds
    handler: python
    options:
        members: true
        show_source: true

#### Examples

```python
# Get power feeds for a rack
rack = nb.dcim.racks.get(name='RACK-01')
feeds = nb.dcim.power_feeds.filter(rack_id=rack.id)

for feed in feeds:
    print(f"{feed.name}: {feed.supply} ({feed.voltage}V)")

# Trace power feed
feed = nb.dcim.power_feeds.get(name='FEED-A')
trace = feed.trace()
```

### Power Outlets and Ports

::: pynetbox.models.dcim.PowerOutlets
    handler: python
    options:
        members: true
        show_source: true

::: pynetbox.models.dcim.PowerPorts
    handler: python
    options:
        members: true
        show_source: true

## Front and Rear Ports

Used for patch panels and pass-through connections.

::: pynetbox.models.dcim.FrontPorts
    handler: python
    options:
        members: true
        show_source: true

::: pynetbox.models.dcim.RearPorts
    handler: python
    options:
        members: true
        show_source: true

## Console Connections

::: pynetbox.models.dcim.ConsolePorts
    handler: python
    options:
        members: true
        show_source: true

::: pynetbox.models.dcim.ConsoleServerPorts
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get console connections for a device
device = nb.dcim.devices.get(name='router1')
console_ports = nb.dcim.console_ports.filter(device_id=device.id)

for port in console_ports:
    print(f"{port.name}: {port.type}")

# Trace console connection
console = nb.dcim.console_ports.get(name='Console', device='router1')
trace = console.trace()
```

## Rack Reservations

::: pynetbox.models.dcim.RackReservations
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Create a rack reservation
reservation = nb.dcim.rack_reservations.create(
    rack=rack_id,
    units=[10, 11, 12],
    description='Reserved for new server',
    user=user_id
)

# List reservations
reservations = nb.dcim.rack_reservations.filter(rack_id=rack.id)
for res in reservations:
    print(res.description)
```
