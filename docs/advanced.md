# Custom Sessions

Custom sessions can be used to modify the default HTTP behavior. Below are a few examples, most of them from [here](https://hodovi.ch/blog/advanced-usage-python-requests-timeouts-retries-hooks/).

## Headers

To set a custom header on all requests. These headers are automatically merged with headers pynetbox sets itself.

Example:

```python
import pynetbox
import requests
session = requests.Session()
session.headers = {"mycustomheader": "test"}
nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
nb.http_session = session
```

## SSL Verification

To disable SSL verification. See [the docs](https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification).

Example:

```python
import pynetbox
import requests
session = requests.Session()
session.verify = False
nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
nb.http_session = session
```

## Timeouts

Setting timeouts requires the use of Adapters.

Example:

```python
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
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)
nb.http_session = session
```

# File Uploads (Image Attachments)

Pynetbox supports file uploads for endpoints that accept them, such as image attachments. When you pass a file-like object (anything with a `.read()` method) to `create()`, pynetbox automatically detects it and uses multipart/form-data encoding instead of JSON.

## Creating an Image Attachment

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)

# Attach an image to a device
with open('/path/to/image.png', 'rb') as f:
    attachment = nb.extras.image_attachments.create(
        object_type='dcim.device',
        object_id=1,
        image=f,
        name='rack-photo.png'
    )
```

## Using io.BytesIO

You can also use in-memory file objects:

```python
import io
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)

# Create image from bytes
image_data = b'...'  # Your image bytes
file_obj = io.BytesIO(image_data)
file_obj.name = 'generated-image.png'  # Optional: set filename

attachment = nb.extras.image_attachments.create(
    object_type='dcim.device',
    object_id=1,
    image=file_obj
)
```

## Custom Filename and Content-Type

For more control, pass a tuple instead of a file object:

```python
with open('/path/to/image.png', 'rb') as f:
    attachment = nb.extras.image_attachments.create(
        object_type='dcim.device',
        object_id=1,
        image=('custom-name.png', f, 'image/png')
    )
```

The tuple format is `(filename, file_object)` or `(filename, file_object, content_type)`.

# Multi-Format Responses

Some endpoints support multiple response formats. The rack elevation endpoint can return both JSON data and SVG diagrams.

## Getting Rack Elevation as JSON

By default, the elevation endpoint returns JSON data as a list of rack unit objects:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f'
)

rack = nb.dcim.racks.get(123)

# Returns list of RU objects (default JSON response)
units = rack.elevation.list()
for unit in units:
    print(unit.id, unit.name)
```

## Getting Rack Elevation as SVG

Use the `render='svg'` parameter to get a graphical SVG diagram:

```python
rack = nb.dcim.racks.get(123)

# Returns raw SVG string
svg_diagram = rack.elevation.list(render='svg')
print(svg_diagram)  # '<svg xmlns="http://www.w3.org/2000/svg">...</svg>'

# Save to file
with open('rack-elevation.svg', 'w') as f:
    f.write(svg_diagram)
```
