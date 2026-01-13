# Wireless

The Wireless module provides models for managing wireless LANs and links in NetBox.

## Overview

The Wireless app includes:

- **Wireless LANs**: WLAN/SSID definitions with custom string representation
- **Wireless LAN Groups**: Logical grouping of WLANs
- **Wireless Links**: Point-to-point wireless connections

## Wireless LANs

The `WirelessLans` model represents wireless LANs (SSIDs) with a custom string representation showing the SSID.

::: pynetbox.models.wireless.WirelessLans
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Basic WLAN Operations

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get a wireless LAN
wlan = nb.wireless.wireless_lans.get(ssid='Corporate-WiFi')
print(wlan)  # Will print the SSID: Corporate-WiFi

# Access WLAN attributes
print(wlan.ssid)
print(wlan.description)
print(wlan.group.name if wlan.group else 'No group')
print(wlan.vlan.vid if wlan.vlan else 'No VLAN')
print(wlan.auth_type)
print(wlan.auth_cipher)

# List all WLANs
wlans = nb.wireless.wireless_lans.all()
for w in wlans:
    print(f"{w.ssid}: {w.auth_type} ({w.auth_cipher})")
```

#### Creating Wireless LANs

```python
# Create a new WLAN
new_wlan = nb.wireless.wireless_lans.create(
    ssid='Guest-WiFi',
    description='Guest wireless network',
    auth_type='wpa-personal',
    auth_cipher='aes',
    status='active'
)

# Create WLAN with VLAN assignment
vlan = nb.ipam.vlans.get(vid=100)
wlan = nb.wireless.wireless_lans.create(
    ssid='Corporate-WiFi',
    description='Corporate wireless network',
    auth_type='wpa-enterprise',
    auth_cipher='aes',
    auth_psk='',  # Not used for enterprise
    vlan=vlan.id,
    status='active'
)

# Create WLAN with group
group = nb.wireless.wireless_lan_groups.get(name='Production')
wlan = nb.wireless.wireless_lans.create(
    ssid='IoT-Network',
    description='IoT devices',
    group=group.id,
    auth_type='wpa-personal',
    auth_cipher='aes',
    auth_psk='YourSecurePassword',
    status='active'
)
```

#### Updating Wireless LANs

```python
# Update WLAN configuration
wlan = nb.wireless.wireless_lans.get(ssid='Guest-WiFi')
wlan.auth_psk = 'NewSecurePassword'
wlan.description = 'Updated guest network'
wlan.save()

# Change VLAN assignment
wlan = nb.wireless.wireless_lans.get(ssid='Corporate-WiFi')
new_vlan = nb.ipam.vlans.get(vid=200)
wlan.vlan = new_vlan.id
wlan.save()
```

## Wireless LAN Groups

```python
# Create a wireless LAN group
group = nb.wireless.wireless_lan_groups.create(
    name='Production',
    slug='production',
    description='Production wireless networks'
)

# Create nested group
child_group = nb.wireless.wireless_lan_groups.create(
    name='Corporate',
    slug='corporate',
    parent=group.id,
    description='Corporate SSIDs'
)

# List all groups
groups = nb.wireless.wireless_lan_groups.all()
for g in groups:
    parent = f" (parent: {g.parent.name})" if g.parent else ""
    print(f"{g.name}{parent}")

# Get WLANs in a group
wlans = nb.wireless.wireless_lans.filter(group_id=group.id)
for wlan in wlans:
    print(f"  {wlan.ssid}")
```

## Wireless Links

Wireless links represent point-to-point wireless connections between devices.

### Examples

```python
# Get devices with wireless interfaces
device_a = nb.dcim.devices.get(name='ap-01')
device_b = nb.dcim.devices.get(name='ap-02')

# Get or create wireless interfaces
interface_a = nb.dcim.interfaces.get(
    device_id=device_a.id,
    name='radio0'
)
interface_b = nb.dcim.interfaces.get(
    device_id=device_b.id,
    name='radio0'
)

# Create a wireless link
link = nb.wireless.wireless_links.create(
    interface_a=interface_a.id,
    interface_b=interface_b.id,
    ssid='BackhaulLink',
    status='active',
    auth_type='wpa-personal',
    auth_cipher='aes',
    auth_psk='SecureBackhaulKey'
)

# Add additional properties
link = nb.wireless.wireless_links.create(
    interface_a=interface_a.id,
    interface_b=interface_b.id,
    ssid='SiteLink',
    status='active',
    description='Site-to-site wireless link',
    auth_type='wpa-enterprise',
    auth_cipher='aes'
)

# List all wireless links
links = nb.wireless.wireless_links.all()
for link in links:
    print(f"{link.ssid}: {link.interface_a} <-> {link.interface_b}")
    print(f"  Status: {link.status}")
    print(f"  Auth: {link.auth_type}/{link.auth_cipher}")
```

## Complete Wireless Deployment Example

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Create WLAN group
group = nb.wireless.wireless_lan_groups.create(
    name='Campus',
    slug='campus',
    description='Campus wireless networks'
)

# Create VLANs for each network
corporate_vlan = nb.ipam.vlans.create(
    name='Corporate-WLAN',
    vid=100,
    site=site.id,
    status='active'
)

guest_vlan = nb.ipam.vlans.create(
    name='Guest-WLAN',
    vid=200,
    site=site.id,
    status='active'
)

iot_vlan = nb.ipam.vlans.create(
    name='IoT-WLAN',
    vid=300,
    site=site.id,
    status='active'
)

# Create wireless LANs
corporate_wlan = nb.wireless.wireless_lans.create(
    ssid='CorpNet',
    description='Corporate wireless network',
    group=group.id,
    vlan=corporate_vlan.id,
    auth_type='wpa-enterprise',
    auth_cipher='aes',
    status='active'
)

guest_wlan = nb.wireless.wireless_lans.create(
    ssid='GuestNet',
    description='Guest wireless network',
    group=group.id,
    vlan=guest_vlan.id,
    auth_type='open',
    status='active'
)

iot_wlan = nb.wireless.wireless_lans.create(
    ssid='IoT-Devices',
    description='IoT device network',
    group=group.id,
    vlan=iot_vlan.id,
    auth_type='wpa-personal',
    auth_cipher='aes',
    auth_psk='IoTDevicePassword',
    status='active'
)

print("Wireless networks deployed:")
print(f"  {corporate_wlan.ssid} - VLAN {corporate_vlan.vid}")
print(f"  {guest_wlan.ssid} - VLAN {guest_vlan.vid}")
print(f"  {iot_wlan.ssid} - VLAN {iot_vlan.vid}")
```

## Filtering and Searching

```python
# Filter by authentication type
wpa_enterprise = nb.wireless.wireless_lans.filter(auth_type='wpa-enterprise')

# Filter by status
active_wlans = nb.wireless.wireless_lans.filter(status='active')

# Filter by group
group_wlans = nb.wireless.wireless_lans.filter(group_id=group.id)

# Filter by VLAN
vlan_wlans = nb.wireless.wireless_lans.filter(vlan_id=vlan.id)

# Search by SSID (case-insensitive)
wlan = nb.wireless.wireless_lans.get(ssid__ic='corporate')

# Complex filters
wlans = nb.wireless.wireless_lans.filter(
    group='campus',
    status='active',
    auth_type='wpa-enterprise'
)

# Wireless links filters
active_links = nb.wireless.wireless_links.filter(status='active')
device_links = nb.wireless.wireless_links.filter(interface_a__device='ap-01')
```

## Authentication Types

NetBox supports the following wireless authentication types:

- **open**: Open network (no authentication)
- **wep**: WEP (deprecated, not recommended)
- **wpa-personal**: WPA/WPA2/WPA3-Personal (PSK)
- **wpa-enterprise**: WPA/WPA2/WPA3-Enterprise (802.1X)

## Authentication Ciphers

Available cipher options:

- **auto**: Automatic cipher selection
- **tkip**: TKIP (deprecated, not recommended)
- **aes**: AES-CCMP (recommended)
- **aes-gcm**: AES-GCM (WPA3)

## Best Practices

1. **Use WPA-Enterprise** for corporate networks with 802.1X authentication
2. **Use AES cipher** for all networks (avoid TKIP)
3. **Assign VLANs** to segregate wireless traffic
4. **Use WLAN Groups** to organize SSIDs by location or purpose
5. **Document PSKs securely** using NetBox's secrets management
6. **Set descriptive names** to make WLAN identification easier
7. **Use status field** to track planned vs active networks
