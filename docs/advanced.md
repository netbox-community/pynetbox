# Advanced Usage

## Threading

PyNetBox supports multithreaded calls for `.filter()` and `.all()` queries to significantly improve performance when fetching large datasets.

!!! warning "NetBox Configuration Required"
    It is **highly recommended** you have `MAX_PAGE_SIZE` in your NetBox installation set to anything *except* `0` or `None`. The default value of `1000` is usually a good value to use.

### Enabling Threading

Enable threading globally by passing `threading=True` to the API initialization:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True
)

# Now all .all() and .filter() calls will use threading
devices = nb.dcim.devices.all()  # Fetches pages in parallel
```

### How It Works

When threading is enabled:
- PyNetBox fetches multiple pages of results in parallel
- Significantly faster for large result sets
- Especially useful for `.all()` queries that span many pages
- Works automatically with pagination

### Example

```python
import pynetbox
import time

nb = pynetbox.api('http://localhost:8000', token='your-token')

# Without threading
start = time.time()
devices = list(nb.dcim.devices.all())
print(f"Without threading: {time.time() - start:.2f}s")

# With threading
nb_threaded = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True
)
start = time.time()
devices = list(nb_threaded.dcim.devices.all())
print(f"With threading: {time.time() - start:.2f}s")
```

## Filter Validation

NetBox doesn't validate filters passed to GET API endpoints (`.get()` and `.filter()`). If a filter is incorrect, NetBox silently returns the entire database table content, which can be slow and unexpected.

PyNetBox can validate filter parameters against NetBox's OpenAPI specification before making the request, raising an exception if a parameter is invalid.

### Enabling Strict Filters Globally

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True  # Enable validation globally
)

# This will raise ParameterValidationError
try:
    devices = nb.dcim.devices.filter(non_existing_filter='value')
except pynetbox.core.query.ParameterValidationError as e:
    print(f"Invalid filter: {e}")
```

### Per-Request Validation

You can also enable or disable validation on a per-request basis:

```python
nb = pynetbox.api('http://localhost:8000', token='your-token')

# Enable for one request (when not globally enabled)
try:
    devices = nb.dcim.devices.filter(
        non_existing_filter='aaaa',
        strict_filters=True
    )
except pynetbox.core.query.ParameterValidationError as e:
    print(f"Invalid filter: {e}")

# Disable for one request (when globally enabled)
nb_strict = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True
)
# This won't raise an exception, but returns entire table
devices = nb_strict.dcim.devices.filter(
    non_existing_filter='aaaa',
    strict_filters=False
)
```

### Benefits of Strict Filters

- **Catch typos early**: Find misspelled filter names before making requests
- **Prevent full table scans**: Avoid accidentally fetching entire tables
- **Better error messages**: Get clear feedback about invalid parameters
- **Development aid**: Helpful during development to ensure correct filter usage

### Example

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True
)

# Valid filter - works fine
devices = nb.dcim.devices.filter(site='datacenter1')

# Invalid filter - raises exception
try:
    devices = nb.dcim.devices.filter(iste='datacenter1')  # Typo: 'iste' instead of 'site'
except pynetbox.core.query.ParameterValidationError as e:
    print(f"Error: {e}")
    # Error: 'iste' is not a valid filter parameter for dcim.devices
```

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
