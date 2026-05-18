# Virtualization

This page documents the special methods available on Virtualization models. Standard CRUD operations follow the patterns described in [Quick Start](getting-started.md) and the [Endpoint reference](endpoint.md).

!!! note "Standard API Operations"
    The standard endpoint methods (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for the available fields and filters on each endpoint.

## Virtual Machines

### Config Rendering

The `render_config` property renders a virtual machine's configuration from its assigned config template and config contexts.

::: pynetbox.models.virtualization.VirtualMachines.render_config
    handler: python
    options:
        show_source: true

**Example:**

```python
vm = nb.virtualization.virtual_machines.get(name='web-vm-01')
config = vm.render_config.create()
print(config)
```
