# Core

This page documents the special methods available on Core models. Standard CRUD operations follow the patterns described in [Quick Start](getting-started.md) and the [Endpoint reference](endpoint.md).

!!! note "Standard API Operations"
    The standard endpoint methods (`.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`) follow NetBox's REST API. Refer to the [NetBox API documentation](https://demo.netbox.dev/api/docs/) for the available fields and filters on each endpoint.

## Data Sources

### Sync

The `sync` property triggers a synchronization of the data source, enqueuing a job to fetch its files from the configured backend (e.g. git, S3).

::: pynetbox.models.core.DataSources.sync
    handler: python
    options:
        show_source: true

**Example:**

```python
data_source = nb.core.data_sources.get(name='config-templates')
data_source.sync.create()
```
