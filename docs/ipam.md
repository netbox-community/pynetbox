# IPAM

This page documents the special methods available on IPAM models. Standard CRUD operations follow the patterns described in [Quick Start](getting-started.md) and the [Endpoint reference](endpoint.md).

!!! note "Standard API Operations"
    The standard endpoint methods (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for the available fields and filters on each endpoint.

## Prefixes

### Available IPs

The `available_ips` property exposes the prefix's `available-ips` detail route, used to list addresses that are not yet allocated and to provision new ones from the available pool.

::: pynetbox.models.ipam.Prefixes.available_ips
    handler: python
    options:
        show_source: true

**Examples:**

```python
prefix = nb.ipam.prefixes.get(prefix='10.0.0.0/24')

# List available IP addresses
available = prefix.available_ips.list()
# [10.0.0.1/24, 10.0.0.2/24, 10.0.0.3/24, ...]

# Provision a single IP from the pool
new_ip = prefix.available_ips.create()

# Provision multiple IPs
new_ips = prefix.available_ips.create([{} for _ in range(5)])

# Provision an IP with specific attributes
new_ip = prefix.available_ips.create({
    'dns_name': 'server01.example.com',
    'description': 'Web Server',
    'status': 'active',
})
```

### Available Prefixes

The `available_prefixes` property exposes the parent prefix's `available-prefixes` detail route, used to list and carve out child prefixes.

::: pynetbox.models.ipam.Prefixes.available_prefixes
    handler: python
    options:
        show_source: true

**Examples:**

```python
prefix = nb.ipam.prefixes.get(prefix='10.0.0.0/16')

# List available child prefixes
available = prefix.available_prefixes.list()
# [10.0.1.0/24, 10.0.2.0/23, 10.0.4.0/22, ...]

# Carve out a single child prefix (prefix_length is required)
new_prefix = prefix.available_prefixes.create({
    'prefix_length': 24,
    'status': 'active',
    'description': 'Server subnet',
})

# Carve out multiple child prefixes
new_prefixes = prefix.available_prefixes.create([
    {'prefix_length': 24},
    {'prefix_length': 24},
    {'prefix_length': 25},
])
```

## IP Ranges

### Available IPs

The `available_ips` property on an IP range works the same way as on a prefix, but allocates from the range's address pool.

::: pynetbox.models.ipam.IpRanges.available_ips
    handler: python
    options:
        show_source: true

**Examples:**

```python
ip_range = nb.ipam.ip_ranges.get(1)

# List available IPs in the range
available = ip_range.available_ips.list()

# Allocate a single IP
new_ip = ip_range.available_ips.create()

# Allocate multiple IPs
new_ips = ip_range.available_ips.create([{} for _ in range(10)])

# Allocate an IP with attributes
new_ip = ip_range.available_ips.create({
    'description': 'DHCP reservation',
    'status': 'reserved',
})
```

## VLAN Groups

### Available VLANs

The `available_vlans` property lists VLAN IDs that are not yet in use within a VLAN group, and allocates new VLANs from that pool.

::: pynetbox.models.ipam.VlanGroups.available_vlans
    handler: python
    options:
        show_source: true

**Examples:**

```python
vlan_group = nb.ipam.vlan_groups.get(name='Production')

# Available VLAN IDs in the group
available = vlan_group.available_vlans.list()
# [10, 11, 12, 13, ...]

# Create a new VLAN; NetBox picks the lowest available VID
new_vlan = vlan_group.available_vlans.create({
    'name': 'NewVLAN',
    'status': 'active',
})

# Create a VLAN with a specific VID (must be available within the group)
new_vlan = vlan_group.available_vlans.create({
    'name': 'Servers',
    'vid': 100,
    'status': 'active',
})
```

## ASN Ranges

### Available ASNs

The `available_asns` property lists ASNs that are not yet allocated within an ASN range, and allocates new ASNs from that pool.

::: pynetbox.models.ipam.AsnRanges.available_asns
    handler: python
    options:
        show_source: true

**Examples:**

```python
asn_range = nb.ipam.asn_ranges.get(name='Private ASN Pool')

# Available ASNs
available = asn_range.available_asns.list()
# [64512, 64513, 64514, ...]

# Allocate a single ASN
new_asn = asn_range.available_asns.create()

# Allocate multiple ASNs
new_asns = asn_range.available_asns.create([{} for _ in range(5)])
```
