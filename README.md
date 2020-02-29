[![Build Status](https://travis-ci.org/digitalocean/pynetbox.svg?branch=master)](https://travis-ci.org/digitalocean/pynetbox)

# Pynetbox
Python API client library for [NetBox](https://github.com/netbox-community/netbox).


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
    private_key_file='/path/to/private-key.pem',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
```

The first argument the .api() method takes is the NetBox URL. There are a handful of named arguments you can provide, but in most cases none are required to simply pull data. In order to write, the `token` argument should to be provided. To decrypt information from the `secrets` endpoint either the `private_key_file` or `private_key` argument needs to be provided.


## Queries

The pynetbox API is setup so that NetBox's apps are attributes of the `.api()` object, and in turn those apps have attribute representing each endpoint. Each endpoint has a handful of verbs available to carry out actions on the endpoint. For example, in order to query all the objects in the devices endpoint you would do the following:

```
nb.dcim.devices.all()
[test1-leaf1, test1-leaf2]
```

### Threading

pynetbox supports multithreaded calls (in Python 3 only) for `.filter()` and `.all()` queries. It is **highly recommended** you have `MAX_PAGE_SIZE` in your Netbox install set to anything *except* `0` or `None`. The default value of `1000` is usually a good value to use. To enable threading, add `threading=True` parameter to the `.api`:

```python
nb = pynetbox.api(
    'http://localhost:8000',
    threading=True,
)
```
