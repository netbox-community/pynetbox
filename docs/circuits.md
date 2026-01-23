# Circuits

This page documents special methods available for Circuits models in pyNetBox.

!!! note "Standard API Operations"
    Standard CRUD operations (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API patterns. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for details on available endpoints and filters.

## Circuit Terminations

### Cable Path Tracing

Circuit terminations support cable path tracing through the `paths()` method. This method returns all cable paths that traverse through the circuit termination, showing the complete connectivity from origin to destination.

**Example:**
```python
# Get a circuit termination
circuit_term = nb.circuits.circuit_terminations.get(circuit_id=123, term_side='A')

# Get all cable paths through this termination
paths = circuit_term.paths()

# Each path contains origin, destination, and path segments
for path_info in paths:
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Example: Find what a circuit connects to
circuit = nb.circuits.circuits.get(cid='CIRCUIT-001')
terminations = nb.circuits.circuit_terminations.filter(circuit_id=circuit.id)

for term in terminations:
    print(f"\nTermination {term.term_side}:")
    paths = term.paths()
    if paths:
        for path in paths:
            if path['destination']:
                print(f"  Connected to: {path['destination']}")
            else:
                print("  No destination (incomplete path)")
    else:
        print("  No cable paths")
```

**Path Structure:**

The `paths()` method returns a list of dictionaries, where each dictionary represents a complete cable path:

- `origin`: The starting endpoint of the path (Record object or None if unconnected)
- `destination`: The ending endpoint of the path (Record object or None if unconnected)
- `path`: A list of path segments, where each segment is a list of Record objects representing the components in that segment (cables, terminations, interfaces, etc.)

## Virtual Circuits

### Overview

Virtual circuits also support cable path tracing through the `paths()` method.

**Example:**
```python
# Get a virtual circuit
vcircuit = nb.circuits.virtual_circuits.get(cid='VPLS-001')
print(f"Virtual Circuit: {vcircuit.cid}")
print(f"Provider Network: {vcircuit.provider_network.name}")
print(f"Type: {vcircuit.type.name}")

# List all terminations for a virtual circuit
terminations = nb.circuits.virtual_circuit_terminations.filter(
    virtual_circuit_id=vcircuit.id
)
for term in terminations:
    print(f"Termination Role: {term.role}")
```

### Virtual Circuit Termination Path Tracing

Virtual circuit terminations also support cable path tracing through the `paths()` method.

**Example:**
```python
# Get a virtual circuit termination
vterm = nb.circuits.virtual_circuit_terminations.get(
    virtual_circuit_id=123, role='hub'
)

# Get all cable paths through this termination
paths = vterm.paths()

# Analyze the connectivity
for path_info in paths:
    print(f"Origin: {path_info['origin']}")
    print(f"Destination: {path_info['destination']}")
    print("Path segments:")
    for segment in path_info['path']:
        for obj in segment:
            print(f"  - {obj}")

# Example: Find all devices connected via a virtual circuit
vcircuit = nb.circuits.virtual_circuits.get(cid='VPLS-001')
terminations = nb.circuits.virtual_circuit_terminations.filter(
    virtual_circuit_id=vcircuit.id
)

print(f"Virtual Circuit {vcircuit.cid} connectivity:")
for term in terminations:
    paths = term.paths()
    if paths and paths[0]['destination']:
        print(f"  {term.role}: {paths[0]['destination']}")
```
