# IPAM

This page documents special methods available for IPAM models in pyNetBox.

!!! note "Standard API Operations"
    Standard CRUD operations (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API patterns. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for details on available endpoints and filters.

## Prefixes

### Available IPs

The `available_ips` property provides access to view and create available IP addresses within a prefix.

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

# Create a single IP from available pool
new_ip = prefix.available_ips.create()

# Create multiple IPs
new_ips = prefix.available_ips.create([{} for i in range(5)])

# Create IP with specific attributes
new_ip = prefix.available_ips.create({
    'dns_name': 'server01.example.com',
    'description': 'Web Server',
    'status': 'active'
})
```

### Available Prefixes

The `available_prefixes` property provides access to view and create available child prefixes within a parent prefix.

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

# Create a child prefix
new_prefix = prefix.available_prefixes.create({
    'prefix_length': 24,
    'status': 'active',
    'description': 'Server subnet'
})

# Create multiple child prefixes
new_prefixes = prefix.available_prefixes.create([
    {'prefix_length': 24},
    {'prefix_length': 24},
    {'prefix_length': 25}
])
```

## IP Ranges

### Available IPs

The `available_ips` property provides access to view and create available IP addresses within an IP range.

::: pynetbox.models.ipam.IpRanges.available_ips
    handler: python
    options:
        show_source: true

**Examples:**
```python
ip_range = nb.ipam.ip_ranges.get(1)

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
```

## VLAN Groups

### Available VLANs

The `available_vlans` property provides access to view and create available VLANs within a VLAN group.

::: pynetbox.models.ipam.VlanGroups.available_vlans
    handler: python
    options:
        show_source: true

**Examples:**
```python
vlan_group = nb.ipam.vlan_groups.get(name='Production')

# List available VLAN IDs
available = vlan_group.available_vlans.list()
# [10, 11, 12, 13, ...]

# Create a VLAN from available IDs
new_vlan = vlan_group.available_vlans.create({
    'name': 'NewVLAN',
    'status': 'active'
})
# NewVLAN (VID: 10)

# Create VLAN with specific VID (must be in available range)
new_vlan = vlan_group.available_vlans.create({
    'name': 'Servers',
    'vid': 100,
    'status': 'active'
})
```

## ASN Ranges

### Available ASNs

The `available_asns` property provides access to view and create available ASNs within an ASN range.

::: pynetbox.models.ipam.AsnRanges.available_asns
    handler: python
    options:
        show_source: true

**Examples:**
```python
asn_range = nb.ipam.asn_ranges.get(name='Private ASN Pool')

# List available ASNs
available = asn_range.available_asns.list()
# [64512, 64513, 64514, ...]

# Allocate a single ASN
new_asn = asn_range.available_asns.create()
# 64512

# Allocate multiple ASNs
new_asns = asn_range.available_asns.create([{} for i in range(5)])
```
