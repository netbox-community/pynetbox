# IPAM (IP Address Management)

The IPAM module provides specialized models for working with IP addresses, prefixes, VLANs, and ASNs in NetBox.

## Overview

The IPAM app includes models with enhanced functionality for:

- **Prefixes**: Prefix allocation with available IP and prefix endpoints
- **IP Ranges**: IP range management with available IP endpoints
- **IP Addresses**: Individual IP address records
- **VLANs**: VLAN management
- **VLAN Groups**: VLAN group management with available VLAN endpoints
- **ASN Ranges**: ASN range management with available ASN endpoints
- **Aggregates**: IP aggregate records

## IP Addresses

The `IpAddresses` model represents individual IP addresses in NetBox.

::: pynetbox.models.ipam.IpAddresses
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get an IP address
ip = nb.ipam.ip_addresses.get(address='10.0.0.1/24')
print(ip.address)
print(ip.status)

# Create an IP address
new_ip = nb.ipam.ip_addresses.create(
    address='10.0.0.50/24',
    status='active',
    dns_name='server01.example.com'
)

# Assign to an interface
ip = nb.ipam.ip_addresses.get(address='10.0.0.50/24')
ip.assigned_object_type = 'dcim.interface'
ip.assigned_object_id = 123
ip.save()

# Filter by VRF
vrf_ips = nb.ipam.ip_addresses.filter(vrf_id=1)
```

## Prefixes

The `Prefixes` model provides methods for viewing available IPs and creating child prefixes.

::: pynetbox.models.ipam.Prefixes
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Working with Available IPs

```python
# Get a prefix
prefix = nb.ipam.prefixes.get(prefix='10.0.0.0/24')

# List available IP addresses
available = prefix.available_ips.list()
print(f"Available IPs: {available}")
# [10.0.0.1/24, 10.0.0.2/24, 10.0.0.3/24, ...]

# Create a single IP from available pool
new_ip = prefix.available_ips.create()
print(new_ip.address)
# 10.0.0.1/24

# Create multiple IPs
new_ips = prefix.available_ips.create([{} for i in range(5)])
for ip in new_ips:
    print(ip.address)
# 10.0.0.2/24
# 10.0.0.3/24
# 10.0.0.4/24
# 10.0.0.5/24
# 10.0.0.6/24

# Create IP with specific attributes
new_ip = prefix.available_ips.create({
    'dns_name': 'server01.example.com',
    'description': 'Web Server',
    'status': 'active'
})
```

#### Working with Available Prefixes

```python
# Get a parent prefix
prefix = nb.ipam.prefixes.get(prefix='10.0.0.0/16')

# List available child prefixes
available = prefix.available_prefixes.list()
print(available)
# [10.0.1.0/24, 10.0.2.0/23, 10.0.4.0/22, ...]

# Create a child prefix
new_prefix = prefix.available_prefixes.create({
    'prefix_length': 24,
    'status': 'active',
    'description': 'Server subnet'
})
print(new_prefix.prefix)
# 10.0.1.0/24

# Create multiple child prefixes
new_prefixes = prefix.available_prefixes.create([
    {'prefix_length': 24},
    {'prefix_length': 24},
    {'prefix_length': 25}
])
```

#### Basic Prefix Operations

```python
# Create a prefix
prefix = nb.ipam.prefixes.create(
    prefix='192.168.1.0/24',
    status='active',
    site=1,
    vlan=10
)

# Update prefix
prefix = nb.ipam.prefixes.get(prefix='192.168.1.0/24')
prefix.description = 'Management Network'
prefix.save()

# Filter prefixes
site_prefixes = nb.ipam.prefixes.filter(site='headquarters')
active_prefixes = nb.ipam.prefixes.filter(status='active')
within_prefix = nb.ipam.prefixes.filter(within='10.0.0.0/8')
```

## IP Ranges

The `IpRanges` model provides methods for working with IP ranges and allocating IPs from them.

::: pynetbox.models.ipam.IpRanges
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get an IP range
ip_range = nb.ipam.ip_ranges.get(1)
print(ip_range.display)
# 10.0.0.1-10.0.0.100

# List available IPs in range
available = ip_range.available_ips.list()

# Create single IP from range
new_ip = ip_range.available_ips.create()

# Create multiple IPs
new_ips = ip_range.available_ips.create([{} for i in range(10)])

# Create IP with attributes
new_ip = ip_range.available_ips.create({
    'description': 'DHCP reservation',
    'status': 'reserved'
})

# Create an IP range
new_range = nb.ipam.ip_ranges.create(
    start_address='10.10.0.1',
    end_address='10.10.0.254',
    status='active',
    description='DHCP Pool'
)
```

## VLANs

The `Vlans` model represents VLANs in NetBox.

::: pynetbox.models.ipam.Vlans
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get a VLAN
vlan = nb.ipam.vlans.get(vid=100)
print(vlan.name)
print(vlan.vid)

# Create a VLAN
new_vlan = nb.ipam.vlans.create(
    name='Servers',
    vid=100,
    status='active',
    site=1
)

# Update VLAN
vlan = nb.ipam.vlans.get(vid=100)
vlan.description = 'Server VLAN'
vlan.save()

# Filter VLANs
site_vlans = nb.ipam.vlans.filter(site='datacenter1')
group_vlans = nb.ipam.vlans.filter(group_id=1)
```

## VLAN Groups

The `VlanGroups` model provides methods for viewing available VLANs and creating VLANs within a group.

::: pynetbox.models.ipam.VlanGroups
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get a VLAN group
vlan_group = nb.ipam.vlan_groups.get(name='Production')

# List available VLAN IDs
available = vlan_group.available_vlans.list()
print(available)
# [10, 11, 12, 13, ...]

# Create a VLAN from available IDs
new_vlan = vlan_group.available_vlans.create({
    'name': 'NewVLAN',
    'status': 'active'
})
print(f"{new_vlan.name} (VID: {new_vlan.vid})")
# NewVLAN (VID: 10)

# Create VLAN with specific VID
new_vlan = vlan_group.available_vlans.create({
    'name': 'Servers',
    'vid': 100,  # Must be in available range
    'status': 'active'
})
```

## ASN Ranges

The `AsnRanges` model provides methods for managing ASN ranges and allocating ASNs.

::: pynetbox.models.ipam.AsnRanges
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get an ASN range
asn_range = nb.ipam.asn_ranges.get(name='Private ASN Pool')

# List available ASNs
available = asn_range.available_asns.list()
print(available)
# [64512, 64513, 64514, ...]

# Allocate a single ASN
new_asn = asn_range.available_asns.create()
print(new_asn.asn)
# 64512

# Allocate multiple ASNs
new_asns = asn_range.available_asns.create([{} for i in range(5)])
for asn in new_asns:
    print(asn.asn)

# Create an ASN range
new_range = nb.ipam.asn_ranges.create(
    name='BGP ASN Pool',
    start=65000,
    end=65100,
    rir=1
)
```

## Aggregates

The `Aggregates` model represents IP aggregates (RIR allocations).

::: pynetbox.models.ipam.Aggregates
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get an aggregate
aggregate = nb.ipam.aggregates.get(prefix='10.0.0.0/8')
print(aggregate.prefix)
print(aggregate.rir.name)

# Create an aggregate
new_aggregate = nb.ipam.aggregates.create(
    prefix='172.16.0.0/12',
    rir=1,  # RIR ID
    description='Private address space'
)

# Filter aggregates
rir_aggregates = nb.ipam.aggregates.filter(rir_id=1)
```

## Additional IPAM Objects

### VRFs

```python
# Working with VRFs
vrf = nb.ipam.vrfs.get(name='PROD')

# Create a VRF
new_vrf = nb.ipam.vrfs.create(
    name='MGMT',
    rd='65000:100',
    description='Management VRF'
)

# Assign prefix to VRF
prefix = nb.ipam.prefixes.get(prefix='192.168.0.0/24')
prefix.vrf = vrf.id
prefix.save()
```

### Route Targets

```python
# Create a route target
rt = nb.ipam.route_targets.create(
    name='65000:100'
)

# Assign to VRF
vrf = nb.ipam.vrfs.get(name='PROD')
vrf.import_targets = [rt.id]
vrf.export_targets = [rt.id]
vrf.save()
```

### Services

```python
# Create a service
service = nb.ipam.services.create(
    name='HTTPS',
    protocol='tcp',
    ports=[443],
    device=device.id
)

# Using service templates
template = nb.ipam.service_templates.get(name='SSH')
service = nb.ipam.services.create(
    device=device.id,
    template=template.id
)
```

### FHRP Groups

```python
# Create an FHRP group
fhrp = nb.ipam.fhrp_groups.create(
    protocol='vrrp',
    group_id=1,
    auth_type='plaintext',
    auth_key='secret'
)

# Assign IPs to FHRP group
assignment = nb.ipam.fhrp_group_assignments.create(
    group=fhrp.id,
    interface_type='dcim.interface',
    interface_id=123,
    priority=100
)
```

## Common IPAM Workflows

### Allocating IPs for New Devices

```python
# Get prefix
prefix = nb.ipam.prefixes.get(prefix='10.0.1.0/24')

# Create IP from available pool
ip = prefix.available_ips.create({
    'dns_name': 'server01.example.com',
    'description': 'Web Server',
    'status': 'active'
})

# Get device interface
interface = nb.dcim.interfaces.get(name='eth0', device='server01')

# Assign IP to interface
ip.assigned_object_type = 'dcim.interface'
ip.assigned_object_id = interface.id
ip.save()

# Set as primary IP
device = nb.dcim.devices.get(name='server01')
device.primary_ip4 = ip.id
device.save()
```

### Subnet Planning

```python
# Get parent prefix
parent = nb.ipam.prefixes.get(prefix='10.0.0.0/16')

# Check available space
available_prefixes = parent.available_prefixes.list()
print(f"Largest available: {available_prefixes[0]}")

# Allocate subnets
subnets = parent.available_prefixes.create([
    {'prefix_length': 24, 'description': 'Web Servers', 'status': 'active'},
    {'prefix_length': 24, 'description': 'Database Servers', 'status': 'active'},
    {'prefix_length': 25, 'description': 'Management', 'status': 'active'}
])

for subnet in subnets:
    print(f"{subnet.prefix} - {subnet.description}")
```
