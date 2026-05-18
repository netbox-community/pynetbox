# Circuits

This page documents the special methods available on Circuits models. Standard CRUD operations follow the patterns described in [Quick Start](getting-started.md) and the [Endpoint reference](endpoint.md).

!!! note "Standard API Operations"
    The standard endpoint methods (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for the available fields and filters on each endpoint.

## Circuit Terminations

### Cable Path Tracing

Circuit terminations support cable path tracing via the `paths()` method. It returns every complete cable path that passes through the termination — from origin to destination, including any intermediate cables and pass-through ports.

**Example:**

```python
# Look up a circuit termination
circuit_term = nb.circuits.circuit_terminations.get(circuit_id=123, term_side='A')

# All cable paths through this termination
for path_info in circuit_term.paths():
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Find what a circuit connects to
circuit = nb.circuits.circuits.get(cid='CIRCUIT-001')
for term in nb.circuits.circuit_terminations.filter(circuit_id=circuit.id):
    print(f"\nTermination {term.term_side}:")
    paths = term.paths()
    if not paths:
        print("  No cable paths")
        continue
    for path in paths:
        if path['destination']:
            print(f"  Connected to: {path['destination']}")
        else:
            print("  No destination (incomplete path)")
```

**Path Structure:**

`paths()` returns a list of dictionaries, one per complete cable path. Each dictionary contains:

- `origin`: The starting endpoint of the path (`Record` or `None` if unconnected).
- `destination`: The ending endpoint of the path (`Record` or `None` if unconnected).
- `path`: A list of path segments. Each segment is a list of `Record` objects representing the components in that segment (cables, terminations, interfaces, etc.).

## Virtual Circuits

Virtual circuits represent L2VPN-like connections delivered over one or more underlying physical circuits.

**Example:**

```python
vcircuit = nb.circuits.virtual_circuits.get(cid='VPLS-001')
print(f"Virtual Circuit: {vcircuit.cid}")
print(f"Provider Network: {vcircuit.provider_network.name}")
print(f"Type: {vcircuit.type.name}")

# All terminations for the virtual circuit
for term in nb.circuits.virtual_circuit_terminations.filter(virtual_circuit_id=vcircuit.id):
    print(f"Termination Role: {term.role}")
```

### Virtual Circuit Termination Path Tracing

Virtual circuit terminations also support cable path tracing via `paths()`, with the same structure as circuit terminations.

**Example:**

```python
vterm = nb.circuits.virtual_circuit_terminations.get(
    virtual_circuit_id=123,
    role='hub',
)

for path_info in vterm.paths():
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Devices connected via a virtual circuit
vcircuit = nb.circuits.virtual_circuits.get(cid='VPLS-001')
print(f"Virtual Circuit {vcircuit.cid} connectivity:")
for term in nb.circuits.virtual_circuit_terminations.filter(virtual_circuit_id=vcircuit.id):
    paths = term.paths()
    if paths and paths[0]['destination']:
        print(f"  {term.role}: {paths[0]['destination']}")
```
