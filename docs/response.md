# Response

This page documents the classes that wrap responses returned by NetBox: `Record` (a single object) and `RecordSet` (a lazy collection of records).

## Record Class

A `Record` represents a single object returned by the NetBox API. API fields are exposed as attributes; nested objects are recursively wrapped as their own `Record` instances. Records returned from a list endpoint are initially "shallow" — accessing an attribute not present in the list response causes pynetbox to fetch the full detail view on demand.

::: pynetbox.core.response.Record
    handler: python
    options:
        members:
            - delete
            - full_details
            - save
            - serialize
            - update
            - updates
        show_source: true
        show_root_heading: true
        heading_level: 3

## RecordSet Class

A `RecordSet` is a one-shot iterator over `Record` objects, returned by `Endpoint.all()` and `Endpoint.filter()`. It pages through results from NetBox on demand. To iterate the results more than once, materialize the set with `list()`.

::: pynetbox.core.response.RecordSet
    handler: python
    options:
        members:
            - delete
            - update
        show_source: true
        show_root_heading: true
        heading_level: 3
