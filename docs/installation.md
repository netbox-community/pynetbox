# Installation

## Requirements

- **Python**: 3.10 or higher
- **NetBox**: 3.3 or higher (for pynetbox 6.7+)
- **Dependencies**:
    - `requests>=2.20.0,<3.0`
    - `packaging`

## Installation Methods

### Install from PyPI (Recommended)

```bash
pip install pynetbox
```

### Install from Source

To install the latest development version directly from GitHub:

```bash
git clone https://github.com/netbox-community/pynetbox.git
cd pynetbox
pip install -e .
```

### Using a Virtual Environment

It is strongly recommended to install pynetbox into a virtual environment so its dependencies are isolated from your system Python:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install pynetbox
pip install pynetbox
```

## Verifying Installation

After installation, verify that pynetbox is importable and check its version:

```python
import pynetbox
print(pynetbox.__version__)
```

You can also test connectivity to your NetBox instance:

```python
import pynetbox

nb = pynetbox.api(
    'http://localhost:8000',
    token='your-api-token-here'
)

# Check NetBox version
print(nb.version)

# Check API status
print(nb.status())
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade pynetbox
```

To install a specific version:

```bash
pip install pynetbox==7.7.0
```

## Development Installation

If you intend to develop or contribute to pynetbox:

```bash
# Clone the repository
git clone https://github.com/netbox-community/pynetbox.git
cd pynetbox

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install runtime and development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pynetbox in editable mode
pip install -e .
```

The integration test suite uses [pytest-docker](https://pypi.org/project/pytest-docker/) to spin up NetBox in containers, so Docker must be installed and running to execute integration tests. Unit tests have no such requirement.

For more information on running the test suite, see the [Development Guide](development/index.md).

## Next Steps

- Read the [Quick Start](getting-started.md) for an introduction to basic usage.
- Explore the [API Reference](api.md) for detailed documentation of core classes.
- Review [Advanced Topics](advanced.md) for threading, filter validation, custom sessions, and file uploads.
