Custom Sessions
===============

Custom sessions can be used to modify the default HTTP behavior. Below are a few examples, most of them from `here <https://hodovi.ch/blog/advanced-usage-python-requests-timeouts-retries-hooks/>`_.

Headers
*******

To set a custom header on all requests. These headers are automatically merged with headers pynetbox sets itself.

:Example:

>>> import pynetbox
>>> import requests
>>> session = requests.Session()
>>> session.headers = {"mycustomheader": "test"}
>>> nb = pynetbox.api(
...     'http://localhost:8000',
...     private_key_file='/path/to/private-key.pem',
...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
... )
>>> nb.http_session = session


SSL Verification
****************

To disable SSL verification. See `the docs <https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification>`_.

:Example:

>>> import pynetbox
>>> import requests
>>> session = requests.Session()
>>> session.verify = False
>>> nb = pynetbox.api(
...     'http://localhost:8000',
...     private_key_file='/path/to/private-key.pem',
...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
... )
>>> nb.http_session = session


Timeouts
********

Setting timeouts requires the use of Adapters.

:Example:

.. code-block:: python

    from requests.adapters import HTTPAdapter

    class TimeoutHTTPAdapter(HTTPAdapter):
        def __init__(self, *args, **kwargs):
            self.timeout = kwargs.get("timeout", 5)
            super().__init__(*args, **kwargs)

        def send(self, request, **kwargs):
            kwargs['timeout'] = self.timeout
            return super().send(request, **kwargs)

    adapter = TimeoutHTTPAdapter()
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    nb = pynetbox.api(
        'http://localhost:8000',
        private_key_file='/path/to/private-key.pem',
        token='d6f4e314a5b5fefd164995169f28ae32d987704f'
    )
    nb.http_session = session

