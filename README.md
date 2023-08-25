# Pynetbox
Python API client library for [NetBox](https://github.com/netbox-community/netbox).

> **Note:** Version 6.7 and later of the library only supports NetBox 3.3 and above.

## Installation

To install run `pip install pynetbox`.

Alternatively, you can clone the repo and run `python setup.py install`.


## Quick Start

The full pynetbox API is documented on [Read the Docs](http://pynetbox.readthedocs.io/en/latest/), but the following should be enough to get started using it.

To begin, import pynetbox and instantiate the API.

```
import pynetbox
nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
```

The first argument the .api() method takes is the NetBox URL. There are a handful of named arguments you can provide, but in most cases none are required to simply pull data. In order to write, the `token` argument should to be provided.


## Queries

The pynetbox API is setup so that NetBox's apps are attributes of the `.api()` object, and in turn those apps have attribute representing each endpoint. Each endpoint has a handful of methods available to carry out actions on the endpoint. For example, in order to query all the objects in the `devices` endpoint you would do the following:

```
>>> devices = nb.dcim.devices.all()
>>> for device in devices:
...     print(device.name)
...
test1-leaf1
test1-leaf2
test1-leaf3
>>>
```

Note that the all() and filter() methods are generators and return an object that can be iterated over only once.  If you are going to be iterating over it repeatedly you need to either call the all() method again, or encapsulate the results in a `list` object like this:
```
>>> devices = list(nb.dcim.devices.all())
```

### Threading

pynetbox supports multithreaded calls for `.filter()` and `.all()` queries. It is **highly recommended** you have `MAX_PAGE_SIZE` in your Netbox install set to anything *except* `0` or `None`. The default value of `1000` is usually a good value to use. To enable threading, add `threading=True` parameter to the `.api`:

```python
nb = pynetbox.api(
    'http://localhost:8000',
    threading=True,
)
```

## Alternative Library

> **Note:** For those interested in a different approach, there is an alternative Python API client library available for NetBox called [netbox-python](https://github.com/netbox-community/netbox-python). This library provides a thin Python wrapper over the NetBox API.

[netbox-python](https://github.com/netbox-community/netbox-python) offers a minimalistic interface to interact with NetBox's API. While it may not provide all the features available in pynetbox, it offers a lightweight and straightforward option for interfacing with NetBox.

To explore further details and access the documentation, please visit the [netbox-python](https://github.com/netbox-community/netbox-python).
