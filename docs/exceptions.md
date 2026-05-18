# Exceptions

pynetbox raises a small set of dedicated exceptions in response to error conditions. They all live in `pynetbox.core.query` and are re-exported at the top level of the `pynetbox` package, so they can also be imported as `pynetbox.RequestError`, `pynetbox.ContentError`, `pynetbox.AllocationError`, and `pynetbox.ParameterValidationError`.

## RequestError

::: pynetbox.core.query.RequestError
    handler: python
    options:
        show_source: true
        show_root_heading: true
        heading_level: 3

## ContentError

::: pynetbox.core.query.ContentError
    handler: python
    options:
        show_source: true
        show_root_heading: true
        heading_level: 3

## AllocationError

::: pynetbox.core.query.AllocationError
    handler: python
    options:
        show_source: true
        show_root_heading: true
        heading_level: 3

## ParameterValidationError

::: pynetbox.core.query.ParameterValidationError
    handler: python
    options:
        show_source: true
        show_root_heading: true
        heading_level: 3

## Example

```python
import pynetbox

nb = pynetbox.api('http://localhost:8000', token='your-token')

try:
    nb.dcim.devices.create(name='destined-for-failure')
except pynetbox.RequestError as e:
    # The error returned by the server is exposed as e.error.
    print(e.error)
```
