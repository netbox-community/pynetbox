# Installation

## Requirements

- **Python**: 3.10 or higher
- **NetBox**: 3.3 or higher (for pyNetBox 6.7+)
- **Dependencies**:
  - `requests>=2.20.0,<3.0`
  - `packaging`

## Installation Methods

### Install from PyPI (Recommended)

The easiest way to install pyNetBox is using pip:

```bash
pip install pynetbox
```

### Install from Source

If you need the latest development version or want to contribute:

```bash
# Clone the repository
git clone https://github.com/netbox-community/pynetbox.git
cd pynetbox

# Install in development mode
pip install -e .

# Or install directly
python setup.py install
```

### Using a Virtual Environment (Recommended)

It's recommended to use a virtual environment to isolate pyNetBox dependencies:

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

After installation, verify pyNetBox is installed correctly:

```python
import pynetbox
print(pynetbox.version)
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

To upgrade to a specific version:

```bash
pip install pynetbox==7.6.0
```

## Development Installation

If you're planning to develop or contribute to pyNetBox:

```bash
# Clone the repository
git clone https://github.com/netbox-community/pynetbox.git
cd pynetbox

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

## Docker Setup for Testing

The test suite requires Docker for integration tests:

```bash
# Ensure Docker is installed and running
docker --version

# Run the test suite
pytest
```

For more information on running tests, see the [Development Guide](development/index.md).

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL certificate errors when connecting to NetBox:

```python
import pynetbox
import requests

# Create a custom session with SSL verification disabled (not recommended for production)
session = requests.Session()
session.verify = False

nb = pynetbox.api(
    'https://netbox.example.com',
    token='your-token',
)
nb.http_session = session
```

### Import Errors

If you get `ImportError: No module named pynetbox`:

1. Ensure pynetbox is installed: `pip list | grep pynetbox`
2. Check you're using the correct Python interpreter
3. Verify your virtual environment is activated (if using one)

### Version Compatibility Issues

If you encounter errors related to NetBox version compatibility:

1. Check your NetBox version: `nb.version`
2. Verify you're using a compatible pyNetBox version (see [compatibility table](index.md#netbox-version-compatibility))
3. Upgrade or downgrade pyNetBox as needed

## Next Steps

- Read the [Getting Started Guide](getting-started.md) for basic usage
- Explore the [API Reference](endpoint.md) for detailed documentation
- Check the [Advanced Topics](advanced.md) for custom configurations
