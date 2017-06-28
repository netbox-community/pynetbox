Pynetbox
----------
Python library for `NetBox <https://github.com/digitalocean/netbox/>`_.


Installation
---------------
pynetbox will be hosted on PyPI. To install run `pip install pynetbox`.

Alternatively, you can clone the repo and run `python setup.py install`.


Quick Start
-----------
The full pynetbox API is documented on `Read the Docs <http://pynetbox.readthedocs.io/en/latest/>`__, but the following should be enough to get started using it.

To begin, import pynetbox and instantiate the API.

::

	import pynetbox
	nb = pynetbox.api(
	    'http://localhost:8000',
	    private_key_file='/path/to/private-key.pem',
	    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
	)

The first argument the .api() method takes is the NetBox URL. There are a handful of named arguments you can provide, but in most cases none are required to simply pull data from NetBox. In order to write, the `token` argument needs to be provided. To decrypt information from the `secrets` endpoint either the `private_key_file` or `private_key` argument needs to be provided.


Queries
-------
The pynetbox API is setup so that NetBox's apps are attributes of the `.api()` object, and in turn those apps have attribute representing each endpoint. Each endpoint has a handful of verbs available to carry out actions on the endpoint. For example, in order to query all the objects in the devices endpoint you would do the following:

::

	nb.dcim.devices.all()
	[test1-leaf1, test1-leaf2]
