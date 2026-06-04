# Advanced Usage

## Threading

pynetbox supports multithreaded page fetching for `.filter()` and `.all()` queries, which can significantly improve performance when iterating large result sets.

!!! warning "NetBox Configuration Required"
    For threading to be effective, `MAX_PAGE_SIZE` in your NetBox installation must be set to a finite value (not `0` or `None`). The default of `1000` is usually a good choice.

### Enabling Threading

Enable threading globally by passing `threading=True` when constructing the API client:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True,
)

# .all() and .filter() now fetch pages in parallel
devices = nb.dcim.devices.all()
```

### How It Works

When threading is enabled, pynetbox issues an initial request to determine the total record count, then dispatches concurrent requests for the remaining pages. The records are streamed back through the same `RecordSet` interface as a single-threaded query.

Threading is opt-in per API client; thread safety beyond pynetbox's own page-fetching is the caller's responsibility.

### Example

```python
import pynetbox
import time

# Single-threaded
nb = pynetbox.api('http://localhost:8000', token='your-token')
start = time.time()
devices = list(nb.dcim.devices.all())
print(f"Without threading: {time.time() - start:.2f}s")

# Multithreaded
nb_threaded = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True,
)
start = time.time()
devices = list(nb_threaded.dcim.devices.all())
print(f"With threading: {time.time() - start:.2f}s")
```

### Tuning the Worker Count

By default, threaded queries use up to 4 worker threads. Override this with `max_workers`:

```python
nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True,
    max_workers=8,
)
```

### Custom Thread Pool Executor

By default pynetbox builds its pool with `concurrent.futures.ThreadPoolExecutor`. You can
inject your own executor with `thread_pool_executor`. It must be a callable matching the
`ThreadPoolExecutor(max_workers=...)` signature and support the context-manager protocol —
a `ThreadPoolExecutor` subclass is the simplest option.

This is useful when worker threads need thread-local state that the standard executor does
not propagate, such as an OpenTelemetry trace context, a request-scoped logging correlation
ID, or a thread-bound database/session handle. Without propagation, work performed in the
pool's threads is detached from the context of the calling thread.

```python
import concurrent.futures
from opentelemetry import context as otel_context

class ContextPropagatingExecutor(concurrent.futures.ThreadPoolExecutor):
    """Carries the caller's OpenTelemetry context into each worker thread."""

    def submit(self, fn, *args, **kwargs):
        ctx = otel_context.get_current()

        def run_with_context():
            token = otel_context.attach(ctx)
            try:
                return fn(*args, **kwargs)
            finally:
                otel_context.detach(token)

        return super().submit(run_with_context)

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    threading=True,
    thread_pool_executor=ContextPropagatingExecutor,
)
```

The executor is constructed once per threaded query and shut down when that query's pages
have been fetched, so pass the class (or a factory), not an already-instantiated pool.

## Filter Validation

NetBox does not validate filter parameters passed to list endpoints. An unrecognized parameter is silently ignored, which means a typo in a `.filter()` or `.get()` call can quietly return the entire table.

pynetbox can optionally validate filter parameters against NetBox's OpenAPI specification before making the request, raising `ParameterValidationError` if any parameter is unrecognized.

### Enabling Strict Filters Globally

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True,
)

try:
    nb.dcim.devices.filter(non_existing_filter='value')
except pynetbox.ParameterValidationError as e:
    print(f"Invalid filter: {e}")
```

### Per-Request Validation

Validation can also be toggled per request by passing `strict_filters` directly to `.filter()` or `.get()`. The per-request value overrides the global setting.

```python
nb = pynetbox.api('http://localhost:8000', token='your-token')

# Enable for one request (when not globally enabled)
try:
    nb.dcim.devices.filter(
        non_existing_filter='aaaa',
        strict_filters=True,
    )
except pynetbox.ParameterValidationError as e:
    print(f"Invalid filter: {e}")

# Disable for one request (when globally enabled)
nb_strict = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True,
)
# Skips validation; NetBox will accept the request but ignore the unknown filter
nb_strict.dcim.devices.filter(
    non_existing_filter='aaaa',
    strict_filters=False,
)
```

!!! note "Custom field filters"
    Custom field filters (`cf_<fieldname>` and their lookup suffixes such as `cf_<fieldname>__gt`) are dynamic and not listed in the OpenAPI specification. They are skipped by the validator and never raise `ParameterValidationError`.

### Benefits

- **Catch typos early**: surface misspelled filter names before they cause silent full-table scans.
- **Better error messages**: failures point to the exact invalid parameter.
- **Safer development**: enable globally during development and disable in production hot paths if needed.

### Example

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-token',
    strict_filters=True,
)

# Valid filter
devices = nb.dcim.devices.filter(site='datacenter1')

# Invalid filter
try:
    devices = nb.dcim.devices.filter(iste='datacenter1')   # typo
except pynetbox.ParameterValidationError as e:
    print(f"Error: {e}")
```

## Custom Sessions

You can substitute pynetbox's default `requests.Session` with your own to customize HTTP behavior such as headers, SSL verification, timeouts, and retries.

### Custom Headers

To set custom headers on every request:

```python
import pynetbox
import requests

session = requests.Session()
session.headers = {'mycustomheader': 'test'}

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)
nb.http_session = session
```

Custom headers are merged with the headers pynetbox sets internally.

### Disabling SSL Verification

To disable SSL certificate verification (for self-signed certificates in lab environments). See the [requests docs](https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification) for additional options:

```python
import pynetbox
import requests

session = requests.Session()
session.verify = False

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)
nb.http_session = session
```

### Timeouts

Setting a default timeout requires a custom HTTP adapter:

```python
import pynetbox
import requests
from requests.adapters import HTTPAdapter


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', 5)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs['timeout'] = self.timeout
        return super().send(request, **kwargs)


adapter = TimeoutHTTPAdapter(timeout=10)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)
nb.http_session = session
```

## File Uploads (Image Attachments)

pynetbox supports file uploads on endpoints that accept them, such as image attachments. When a file-like object (anything with a callable `.read()`) is passed to `.create()`, pynetbox automatically switches to `multipart/form-data` encoding instead of JSON.

### Creating an Image Attachment

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)

with open('/path/to/image.png', 'rb') as f:
    attachment = nb.extras.image_attachments.create(
        object_type='dcim.device',
        object_id=1,
        image=f,
        name='rack-photo.png',
    )
```

### Using `io.BytesIO`

In-memory file objects work the same way:

```python
import io
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)

image_data = b'...'   # raw image bytes
file_obj = io.BytesIO(image_data)
file_obj.name = 'generated-image.png'   # optional: filename hint

attachment = nb.extras.image_attachments.create(
    object_type='dcim.device',
    object_id=1,
    image=file_obj,
)
```

### Custom Filename and Content-Type

For full control over the multipart part, pass a tuple in place of the file object. The accepted forms are `(filename, file_object)` and `(filename, file_object, content_type)`:

```python
with open('/path/to/image.png', 'rb') as f:
    attachment = nb.extras.image_attachments.create(
        object_type='dcim.device',
        object_id=1,
        image=('custom-name.png', f, 'image/png'),
    )
```

## Multi-Format Responses

Some endpoints can return data in multiple formats. The rack elevation endpoint, for example, supports both JSON (a list of rack-unit objects) and SVG (a rendered diagram).

### Rack Elevation as JSON

By default the elevation endpoint returns JSON:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='d6f4e314a5b5fefd164995169f28ae32d987704f',
)

rack = nb.dcim.racks.get(123)

# Returns a list of RU objects
for unit in rack.elevation.list():
    print(unit.id, unit.name)
```

### Rack Elevation as SVG

Pass `render='svg'` to get a rendered SVG diagram as a string:

```python
rack = nb.dcim.racks.get(123)

svg_diagram = rack.elevation.list(render='svg')
# '<svg xmlns="http://www.w3.org/2000/svg">...</svg>'

with open('rack-elevation.svg', 'w') as f:
    f.write(svg_diagram)
```
