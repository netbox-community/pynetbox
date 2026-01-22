# Virtualization

This page documents special methods available for Virtualization models in pyNetBox.

!!! note "Standard API Operations"
    Standard CRUD operations (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API patterns. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for details on available endpoints and filters.

## Virtual Machines

### Config Rendering

The `render_config` property renders virtual machine configuration based on config contexts and templates.

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
