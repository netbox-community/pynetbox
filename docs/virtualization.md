# Virtualization

The Virtualization module provides specialized models for working with virtual machines and clusters in NetBox.

## Overview

The Virtualization app includes:

- **Virtual Machines**: VM objects with config rendering support
- **Clusters**: Virtualization cluster management
- **Cluster Types**: Type definitions for clusters
- **Cluster Groups**: Logical grouping of clusters
- **Virtual Interfaces**: Network interfaces for VMs
- **Virtual Disks**: Storage for VMs

## Virtual Machines

The `VirtualMachines` model provides special methods for VM configuration rendering.

::: pynetbox.models.virtualization.VirtualMachines
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Basic VM Operations

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get a virtual machine
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')

# Access VM attributes
print(vm.name)
print(vm.status)
print(vm.vcpus)
print(vm.memory)
print(vm.disk)
print(vm.cluster.name)

# Access primary IPs
if vm.primary_ip4:
    print(f"IPv4: {vm.primary_ip4.address}")
if vm.primary_ip6:
    print(f"IPv6: {vm.primary_ip6.address}")
```

#### Creating Virtual Machines

```python
# Create a new VM
new_vm = nb.virtualization.virtual_machines.create(
    name='app-vm-01',
    cluster=1,  # Cluster ID
    status='active',
    vcpus=4,
    memory=8192,  # MB
    disk=100  # GB
)

# Create VM with more details
vm = nb.virtualization.virtual_machines.create(
    name='db-vm-01',
    cluster=cluster.id,
    status='active',
    site=site.id,
    role=role.id,
    platform=platform.id,
    vcpus=8,
    memory=16384,
    disk=500,
    description='PostgreSQL Database Server'
)
```

#### Updating Virtual Machines

```python
# Update VM resources
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')
vm.vcpus = 8
vm.memory = 16384
vm.save()

# Update multiple fields
vm.update({
    'vcpus': 8,
    'memory': 16384,
    'disk': 200,
    'description': 'Updated web server'
})
```

#### Config Rendering

```python
# Render VM configuration
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')
config = vm.render_config.create()
print(config)
```

#### Working with Config Context

```python
# Access config context (read-only, inherited from cluster/site/etc)
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')
print(vm.config_context)
# {'dns_servers': ['10.0.0.1', '10.0.0.2'], ...}

# Access local context data (specific to this VM)
print(vm.local_context_data)

# Update local context data
vm.local_context_data = {
    'app_env': 'production',
    'backup_enabled': True,
    'monitoring': {
        'enabled': True,
        'interval': 60
    }
}
vm.save()
```

### Assigning IPs to VMs

```python
# Get or create an IP for the VM
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')

# Create VM interface
interface = nb.virtualization.interfaces.create(
    virtual_machine=vm.id,
    name='eth0',
    enabled=True
)

# Assign an IP to the interface
ip = nb.ipam.ip_addresses.create(
    address='10.0.1.50/24',
    status='active',
    assigned_object_type='virtualization.vminterface',
    assigned_object_id=interface.id,
    dns_name='web-vm-01.example.com'
)

# Set as primary IP
vm.primary_ip4 = ip.id
vm.save()
```

## Clusters

### Basic Cluster Operations

```python
# Get a cluster
cluster = nb.virtualization.clusters.get(name='VMWARE-CLUSTER-01')
print(cluster.name)
print(cluster.type.name)
print(cluster.group.name if cluster.group else "No group")

# Create a cluster
new_cluster = nb.virtualization.clusters.create(
    name='VMWARE-CLUSTER-02',
    type=cluster_type.id,
    group=cluster_group.id,
    site=site.id,
    status='active'
)

# List all VMs in a cluster
vms = nb.virtualization.virtual_machines.filter(cluster_id=cluster.id)
for vm in vms:
    print(f"  {vm.name}: {vm.status}")
```

### Cluster Types

```python
# Create a cluster type
cluster_type = nb.virtualization.cluster_types.create(
    name='VMware ESXi',
    slug='vmware-esxi'
)

# List all cluster types
types = nb.virtualization.cluster_types.all()
for ct in types:
    print(f"{ct.name} ({ct.slug})")
```

### Cluster Groups

```python
# Create a cluster group
cluster_group = nb.virtualization.cluster_groups.create(
    name='Production',
    slug='production',
    description='Production virtualization clusters'
)

# List clusters in a group
clusters = nb.virtualization.clusters.filter(group_id=cluster_group.id)
```

## Virtual Interfaces

```python
# Create a VM interface
interface = nb.virtualization.interfaces.create(
    virtual_machine=vm.id,
    name='eth0',
    enabled=True,
    mtu=1500,
    description='Primary network interface'
)

# Create interface with MAC address
interface = nb.virtualization.interfaces.create(
    virtual_machine=vm.id,
    name='eth1',
    enabled=True,
    mac_address='00:50:56:ab:cd:ef'
)

# Update interface
interface = nb.virtualization.interfaces.get(name='eth0', virtual_machine_id=vm.id)
interface.enabled = False
interface.description = 'Disabled interface'
interface.save()

# List all interfaces for a VM
interfaces = nb.virtualization.interfaces.filter(virtual_machine_id=vm.id)
for iface in interfaces:
    print(f"{iface.name}: {'Enabled' if iface.enabled else 'Disabled'}")
```

## Virtual Disks

```python
# Create a virtual disk
disk = nb.virtualization.virtual_disks.create(
    virtual_machine=vm.id,
    name='disk1',
    size=100,  # GB
    description='Primary storage'
)

# Create additional disk
disk2 = nb.virtualization.virtual_disks.create(
    virtual_machine=vm.id,
    name='disk2',
    size=500,
    description='Data storage'
)

# List all disks for a VM
disks = nb.virtualization.virtual_disks.filter(virtual_machine_id=vm.id)
total_storage = sum(disk.size for disk in disks)
print(f"Total storage: {total_storage} GB")
```

## Complete VM Deployment Example

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get required objects
cluster = nb.virtualization.clusters.get(name='PROD-CLUSTER')
site = nb.dcim.sites.get(name='datacenter1')
role = nb.dcim.device_roles.get(name='server')
platform = nb.dcim.platforms.get(name='linux')

# Create the VM
vm = nb.virtualization.virtual_machines.create(
    name='app-server-01',
    cluster=cluster.id,
    site=site.id,
    role=role.id,
    platform=platform.id,
    status='active',
    vcpus=4,
    memory=8192,
    disk=100,
    description='Application Server',
    comments='Deployed via pynetbox'
)

# Create network interface
interface = nb.virtualization.interfaces.create(
    virtual_machine=vm.id,
    name='eth0',
    enabled=True
)

# Get available IP from prefix
prefix = nb.ipam.prefixes.get(prefix='10.0.1.0/24')
ip = prefix.available_ips.create({
    'assigned_object_type': 'virtualization.vminterface',
    'assigned_object_id': interface.id,
    'dns_name': f'{vm.name}.example.com',
    'status': 'active'
})

# Set as primary IP
vm.primary_ip4 = ip.id
vm.save()

# Add local context data
vm.local_context_data = {
    'environment': 'production',
    'backup_schedule': 'daily',
    'monitoring_enabled': True
}
vm.save()

print(f"VM {vm.name} deployed successfully")
print(f"  IP: {ip.address}")
print(f"  Cluster: {cluster.name}")
print(f"  Resources: {vm.vcpus} vCPUs, {vm.memory} MB RAM, {vm.disk} GB disk")
```

## Filtering and Searching

```python
# Filter by cluster
cluster_vms = nb.virtualization.virtual_machines.filter(cluster='prod-cluster')

# Filter by status
active_vms = nb.virtualization.virtual_machines.filter(status='active')

# Filter by site
site_vms = nb.virtualization.virtual_machines.filter(site='datacenter1')

# Filter by role
web_servers = nb.virtualization.virtual_machines.filter(role='web-server')

# Filter by platform
linux_vms = nb.virtualization.virtual_machines.filter(platform='linux')

# Complex filters
vms = nb.virtualization.virtual_machines.filter(
    cluster='prod-cluster',
    status='active',
    site='datacenter1'
)

# Filter by custom fields
tagged_vms = nb.virtualization.virtual_machines.filter(tag='production')
```
