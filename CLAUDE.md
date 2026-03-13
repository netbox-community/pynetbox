# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pynetbox is a Python API client library for NetBox. It provides a Pythonic interface to interact with NetBox's REST API, supporting NetBox 3.3 and above (pynetbox 6.7+).

## Development Commands

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

The test suite requires Docker to be installed and running for integration tests.

```bash
# Run all tests
pytest

# Run only unit tests (fast, no Docker required)
pytest tests/unit

# Run only integration tests (requires Docker)
pytest tests/integration

# Run specific test file
pytest tests/unit/test_api.py

# Run specific test function
pytest tests/unit/test_api.py::test_api_status

# Run tests matching a pattern
pytest -k "test_api"

# Run with coverage
pytest --cov=pynetbox tests/
```

### Integration Tests - Version Control

Integration tests can be run against specific NetBox versions:

```bash
# Test against specific NetBox versions (default: 4.4)
pytest tests/integration --netbox-versions 4.4

# Skip cleanup to leave Docker containers running
pytest --no-cleanup

# Use existing NetBox instance (skip Docker)
pytest -p no:docker --url-override http://localhost:8000
```

### Code Formatting

```bash
# Format code with Black
black .

# Check formatting without changes
black --check .
```

### Building Documentation

```bash
# Build and serve docs locally
mkdocs serve

# Deploy docs to GitHub Pages
mkdocs gh-deploy
```

## Architecture

### Core Module Structure

The codebase follows a layered architecture:

1. **API Layer** (`pynetbox/core/api.py`):
   - `Api` class is the main entry point
   - Initializes NetBox app endpoints (dcim, ipam, circuits, virtualization, extras, users, wireless, core, vpn, tenancy)
   - Supports `plugins` via `PluginsApp` for accessing NetBox plugin APIs
   - Manages HTTP session, authentication tokens, threading, and strict filter validation

2. **App Layer** (`pynetbox/core/app.py`):
   - `App` class represents NetBox applications (dcim, ipam, etc.)
   - Dynamic attribute access returns `Endpoint` objects
   - `PluginsApp` handles plugin namespacing with dashes converted to underscores

3. **Endpoint Layer** (`pynetbox/core/endpoint.py`):
   - `Endpoint` class provides CRUD operations for API endpoints
   - Methods: `.all()`, `.filter()`, `.get()`, `.create()`, `.update()`, `.delete()`, `.choices()`
   - Handles parameter validation against OpenAPI spec when `strict_filters=True`
   - Converts underscores to dashes in endpoint names (e.g., `ip_addresses` → `ip-addresses`)

4. **Query Layer** (`pynetbox/core/query.py`):
   - `Request` class handles HTTP communication
   - Supports threading for `.all()` and `.filter()` operations
   - Custom exceptions: `RequestError`, `AllocationError`, `ContentError`, `ParameterValidationError`

5. **Response Layer** (`pynetbox/core/response.py`):
   - `Record` class represents individual API objects
   - `RecordSet` class for collections (iterable, returned by `.all()` and `.filter()`)
   - Records support dict-like access, attribute access, and serialization
   - `.save()` method for updating objects, `.delete()` for deletion

### Models Module Structure

Custom Record classes in `pynetbox/models/` provide specialized behavior for specific endpoints:

- `dcim.py`: DCIM-specific models (Devices, Interfaces, Cables with tracing, etc.)
- `ipam.py`: IP address management (IpAddresses, Prefixes, VLANs, etc.)
- `circuits.py`: Circuit models
- `virtualization.py`: Virtual machine models
- `extras.py`: Custom fields, tags, webhooks
- `users.py`: User and permission models
- `wireless.py`: Wireless endpoint models
- `core.py`: DataSources, Jobs, ObjectChanges models
- `mapper.py`: `CONTENT_TYPE_MAPPER` maps NetBox content-type strings (e.g. `"dcim.device"`) to their custom Record classes; used when resolving polymorphic nested objects

### Key Design Patterns

1. **Lazy Loading**: Endpoints and apps are created on attribute access, not initialization
2. **Threading Support**: Enable with `threading=True` in API initialization for parallel pagination
3. **Custom Sessions**: Override `api.http_session` for custom SSL, timeouts, retries
4. **Branch Support**: Context manager `api.activate_branch()` for NetBox branching plugin
5. **Filter Validation**: `strict_filters=True` validates parameters against OpenAPI spec before requests

## Important Implementation Details

### Serialization for API Requests

When preparing objects for POST/PUT/PATCH operations, pynetbox automatically handles:
- Nested objects are reduced to IDs or simple values
- Custom fields are flattened
- Tags and certain list fields are treated as sets, not ordered lists
- Use `.serialize()` method to see how an object will be sent to the API

### Cable Terminations and Complex Objects

Some NetBox objects like Cables have complex nested structures. The `dcim.py` models contain specialized handling:
- `TraceableRecord`: Base class for objects that support cable tracing
- `Cables`: Handles A/B terminations with proper serialization
- DetailEndpoints vs regular Endpoints for objects without list views

### Test Structure

- `tests/test_*.py`: Older-style unit tests (circuits, tenancy, users, virtualization, wireless, api, app)
- `tests/unit/`: Newer unit tests that mock HTTP responses
- `tests/integration/`: Integration tests against real NetBox instances in Docker
- `tests/conftest.py`: Shared pytest configuration and fixtures (defines `--netbox-versions`, `--no-cleanup`, `--url-override` options)
- `tests/integration/conftest.py`: Docker setup for spinning up NetBox containers

The integration test framework uses `pytest-docker` to:
1. Pull and launch netbox-docker containers
2. Wait for NetBox to be ready
3. Run tests against the live instance
4. Clean up containers after tests (unless `--no-cleanup` specified)

## Branching and Git Workflow

- Main branch: `master`
- Current working branch visible in git status
- Commit messages should prefix with "Fixes" or "Closes" and issue number (e.g., "Closes #1234: Add IPv5 support")
- Pull requests require approval for accepted issues only (trivial documentation changes excepted)

## Version Compatibility

Current version: 7.6.1

NetBox version compatibility is strict:
- pynetbox 7.6.1 supports NetBox 4.5.0
- pynetbox 7.5.0 supports NetBox 4.1, 4.2, 4.3
- pynetbox 7.4.1 supports NetBox 4.0.6
- pynetbox 7.0.0+ requires NetBox 3.3+

When working on features, verify compatibility with the supported NetBox versions via integration tests.
