# Circuits

The Circuits module provides models for managing provider circuits and circuit terminations in NetBox.

## Overview

The Circuits app includes:

- **Circuits**: Circuit records with custom string representation
- **Circuit Terminations**: Endpoints of circuits
- **Providers**: Service providers
- **Provider Accounts**: Account information for providers
- **Provider Networks**: Provider network definitions
- **Circuit Types**: Circuit type classifications
- **Circuit Groups**: Logical grouping of circuits
- **Circuit Group Assignments**: Assignment of circuits to groups

## Circuits

The `Circuits` model represents circuits with a custom string representation showing the circuit ID (CID).

::: pynetbox.models.circuits.Circuits
    handler: python
    options:
        members: true
        show_source: true

### Examples

#### Basic Circuit Operations

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get a circuit
circuit = nb.circuits.circuits.get(cid='CIRCUIT-12345')
print(circuit)  # Will print the CID: CIRCUIT-12345

# Access circuit attributes
print(circuit.cid)
print(circuit.type.name)
print(circuit.provider.name)
print(circuit.status)
print(circuit.commit_rate)  # in Kbps

# List all circuits
circuits = nb.circuits.circuits.all()
for c in circuits:
    print(f"{c.cid}: {c.provider.name} - {c.type.name}")
```

#### Creating Circuits

```python
# Get provider and circuit type
provider = nb.circuits.providers.get(name='AT&T')
circuit_type = nb.circuits.circuit_types.get(name='Internet')

# Create a new circuit
new_circuit = nb.circuits.circuits.create(
    cid='CIRCUIT-67890',
    provider=provider.id,
    type=circuit_type.id,
    status='active',
    commit_rate=1000000,  # 1 Gbps in Kbps
    description='Primary Internet Circuit'
)

# Create circuit with installation date
from datetime import date

circuit = nb.circuits.circuits.create(
    cid='MPLS-001',
    provider=provider.id,
    type=circuit_type.id,
    status='active',
    install_date=date.today().isoformat(),
    commit_rate=100000,  # 100 Mbps
    description='MPLS WAN Circuit'
)
```

#### Updating Circuits

```python
# Update circuit information
circuit = nb.circuits.circuits.get(cid='CIRCUIT-12345')
circuit.commit_rate = 2000000  # Upgrade to 2 Gbps
circuit.description = 'Upgraded Internet Circuit'
circuit.save()

# Update status
circuit.status = 'planned'
circuit.save()
```

## Circuit Terminations

The `CircuitTerminations` model represents the endpoints of circuits with custom string representation.

::: pynetbox.models.circuits.CircuitTerminations
    handler: python
    options:
        members: true
        show_source: true

### Examples

```python
# Get circuit terminations for a circuit
circuit = nb.circuits.circuits.get(cid='CIRCUIT-12345')
terminations = nb.circuits.circuit_terminations.filter(circuit_id=circuit.id)

for term in terminations:
    print(f"{term.term_side}: {term.site.name if term.site else 'No site'}")
    if term.port_speed:
        print(f"  Port Speed: {term.port_speed} Kbps")
    if term.upstream_speed:
        print(f"  Upstream: {term.upstream_speed} Kbps")

# Create termination for A-side
term_a = nb.circuits.circuit_terminations.create(
    circuit=circuit.id,
    term_side='A',
    site=site_a.id,
    port_speed=1000000,  # 1 Gbps
    upstream_speed=1000000,
    xconnect_id='XCON-A-001',
    description='Datacenter A termination'
)

# Create termination for Z-side
term_z = nb.circuits.circuit_terminations.create(
    circuit=circuit.id,
    term_side='Z',
    site=site_z.id,
    port_speed=1000000,
    upstream_speed=1000000,
    xconnect_id='XCON-Z-001',
    description='Datacenter B termination'
)
```

## Providers

```python
# Get a provider
provider = nb.circuits.providers.get(name='Verizon')
print(provider.name)
print(provider.asns)  # List of ASNs

# Create a provider
new_provider = nb.circuits.providers.create(
    name='CenturyLink',
    slug='centurylink',
    asns=[65000, 65001],
    portal_url='https://portal.centurylink.com',
    noc_contact='noc@centurylink.com',
    admin_contact='admin@centurylink.com'
)

# Update provider
provider = nb.circuits.providers.get(name='CenturyLink')
provider.comments = 'Updated contact information'
provider.save()

# List all providers
providers = nb.circuits.providers.all()
for p in providers:
    print(f"{p.name} (ASNs: {p.asns})")
```

## Provider Accounts

```python
# Create a provider account
account = nb.circuits.provider_accounts.create(
    provider=provider.id,
    name='ACC-001',
    account='12345-67890',
    description='Primary account'
)

# Get provider accounts
accounts = nb.circuits.provider_accounts.filter(provider_id=provider.id)
for acc in accounts:
    print(f"{acc.name}: {acc.account}")

# Update account
account = nb.circuits.provider_accounts.get(name='ACC-001')
account.description = 'Updated account info'
account.save()
```

## Provider Networks

```python
# Create a provider network
network = nb.circuits.provider_networks.create(
    provider=provider.id,
    name='MPLS-CORE',
    description='Provider MPLS core network'
)

# Get provider networks
networks = nb.circuits.provider_networks.filter(provider_id=provider.id)
for net in networks:
    print(f"{net.name}: {net.description}")

# Associate circuit with provider network
circuit = nb.circuits.circuits.get(cid='MPLS-001')
# Note: provider_network is typically set on circuit terminations
term = nb.circuits.circuit_terminations.get(circuit_id=circuit.id, term_side='A')
# Provider network field depends on NetBox version
```

## Circuit Types

```python
# Create a circuit type
circuit_type = nb.circuits.circuit_types.create(
    name='Dark Fiber',
    slug='dark-fiber',
    description='Dark fiber circuits'
)

# List all circuit types
types = nb.circuits.circuit_types.all()
for ct in types:
    print(ct.name)

# Get circuits of a specific type
internet_circuits = nb.circuits.circuits.filter(type='internet')
```

## Circuit Groups

```python
# Create a circuit group
group = nb.circuits.circuit_groups.create(
    name='Internet Circuits',
    slug='internet-circuits',
    description='All internet connectivity circuits'
)

# List all circuit groups
groups = nb.circuits.circuit_groups.all()
for g in groups:
    print(f"{g.name}: {g.description}")
```

## Circuit Group Assignments

```python
# Assign a circuit to a group
assignment = nb.circuits.circuit_group_assignments.create(
    circuit=circuit.id,
    group=group.id,
    priority='primary'
)

# Get all circuits in a group
assignments = nb.circuits.circuit_group_assignments.filter(group_id=group.id)
for assign in assignments:
    circuit = nb.circuits.circuits.get(assign.circuit.id)
    print(f"{circuit.cid}: {assign.priority}")

# Remove assignment
assignment.delete()
```

## Complete Circuit Deployment Example

```python
import pynetbox
from datetime import date

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Get or create provider
provider = nb.circuits.providers.get(name='AT&T')
if not provider:
    provider = nb.circuits.providers.create(
        name='AT&T',
        slug='att',
        asns=[7018]
    )

# Get or create circuit type
circuit_type = nb.circuits.circuit_types.get(name='Internet')
if not circuit_type:
    circuit_type = nb.circuits.circuit_types.create(
        name='Internet',
        slug='internet'
    )

# Create the circuit
circuit = nb.circuits.circuits.create(
    cid='ATT-INET-12345',
    provider=provider.id,
    type=circuit_type.id,
    status='active',
    install_date=date.today().isoformat(),
    commit_rate=10000000,  # 10 Gbps
    description='Primary Internet - 10G'
)

# Get sites
site_a = nb.dcim.sites.get(name='Datacenter-A')
site_z = nb.dcim.sites.get(name='Datacenter-B')

# Create A-side termination
term_a = nb.circuits.circuit_terminations.create(
    circuit=circuit.id,
    term_side='A',
    site=site_a.id,
    port_speed=10000000,
    upstream_speed=10000000,
    description='A-side at Datacenter-A'
)

# Create Z-side termination
term_z = nb.circuits.circuit_terminations.create(
    circuit=circuit.id,
    term_side='Z',
    site=site_z.id,
    port_speed=10000000,
    upstream_speed=10000000,
    description='Z-side at Datacenter-B'
)

print(f"Circuit {circuit.cid} deployed successfully")
print(f"  Provider: {provider.name}")
print(f"  Type: {circuit_type.name}")
print(f"  Commit Rate: {circuit.commit_rate} Kbps")
print(f"  A-side: {site_a.name}")
print(f"  Z-side: {site_z.name}")
```

## Filtering and Searching

```python
# Filter by provider
att_circuits = nb.circuits.circuits.filter(provider='att')

# Filter by status
active_circuits = nb.circuits.circuits.filter(status='active')

# Filter by type
mpls_circuits = nb.circuits.circuits.filter(type='mpls')

# Filter by site (via terminations)
site = nb.dcim.sites.get(name='Datacenter-A')
terminations = nb.circuits.circuit_terminations.filter(site_id=site.id)
circuit_ids = [t.circuit.id for t in terminations]

# Complex search
circuits = nb.circuits.circuits.filter(
    provider='att',
    status='active',
    type='internet'
)

# Search by CID
circuit = nb.circuits.circuits.get(cid__ic='12345')  # Case-insensitive contains
```

## Working with Circuit Connectivity

```python
# Get circuit and its terminations
circuit = nb.circuits.circuits.get(cid='CIRCUIT-12345')
terminations = nb.circuits.circuit_terminations.filter(circuit_id=circuit.id)

# Check both ends
for term in terminations:
    print(f"\n{term.term_side}-side:")
    print(f"  Site: {term.site.name if term.site else 'Not assigned'}")
    print(f"  Port Speed: {term.port_speed} Kbps")

    # Get connected interface if present
    # Note: This depends on how your circuits are cabled
    if hasattr(term, 'cable') and term.cable:
        print(f"  Cable: {term.cable}")
```
