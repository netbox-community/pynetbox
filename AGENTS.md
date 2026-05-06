# AGENTS.md — pynetbox

## Repository Overview

`pynetbox` is a Python API client library for NetBox. It provides a Pythonic interface to interact with NetBox's REST API and supports NetBox 3.3+ (pynetbox 6.7+). It is a standalone library — not a Django app or NetBox plugin — published to PyPI and used by automation tooling, scripts, and other Python projects to read and write NetBox data. Current version: `7.7.0` (see `pynetbox/__init__.py`).

## Tech Stack

- Python 3.10+ (tested on 3.12, 3.13, 3.14 in CI)
- `requests` + `urllib3` for HTTP (pins in `requirements.txt`)
- `packaging` for version comparisons
- `pytest` + `pytest-docker` for the test suite (unit and integration)
- `ruff` for linting (no `ruff.toml`; configured inline or with defaults)
- `mkdocs-material` + `mkdocstrings` for user-facing docs

Defer all version pins to `requirements.txt` and `requirements-dev.txt`. Package metadata lives in `setup.py` (uses `setuptools_scm` for version from git tags).

## Repository Map

```text
.
├── pynetbox/
│   ├── __init__.py              — Public API: Api, exceptions, __version__.
│   ├── core/
│   │   ├── api.py               — Api class: entry point, session management, app init.
│   │   ├── app.py               — App and PluginsApp: dynamic endpoint access.
│   │   ├── endpoint.py          — Endpoint: CRUD operations, filter validation.
│   │   ├── query.py             — Request: HTTP layer, threading, exceptions.
│   │   ├── response.py          — Record, RecordSet: deserialization, save/delete.
│   │   └── util.py              — Shared utilities.
│   └── models/
│       ├── circuits.py          — Circuit-specific Record subclasses.
│       ├── core.py              — DataSources, Jobs, ObjectChanges models.
│       ├── dcim.py              — DCIM models: Devices, Interfaces, Cables, tracing.
│       ├── extras.py            — Custom fields, tags, webhooks.
│       ├── ipam.py              — IP address management: IpAddresses, Prefixes, VLANs.
│       ├── mapper.py            — CONTENT_TYPE_MAPPER: content-type string → Record class.
│       ├── users.py             — User and permission models.
│       ├── virtualization.py    — Virtual machine models.
│       └── wireless.py          — Wireless endpoint models.
├── tests/
│   ├── conftest.py              — Pytest options: --netbox-versions, --no-cleanup, --url-override.
│   ├── fixtures/                — JSON response fixtures for unit tests (organised by app).
│   ├── test_api.py              — Api-level unit tests.
│   ├── test_app.py              — App/PluginsApp unit tests.
│   ├── test_circuits.py         — Circuits unit tests (older style).
│   ├── test_dcim.py             — DCIM unit tests (older style).
│   ├── test_tenancy.py          — Tenancy unit tests.
│   ├── test_users.py            — Users unit tests.
│   ├── test_virtualization.py   — Virtualization unit tests.
│   ├── test_wireless.py         — Wireless unit tests.
│   ├── util.py                  — Shared test helpers.
│   ├── unit/                    — Newer unit tests (mock HTTP responses).
│   │   ├── test_detailendpoint.py
│   │   ├── test_endpoint.py
│   │   ├── test_endpoint_strict_filter.py
│   │   ├── test_extras.py
│   │   ├── test_file_upload.py
│   │   ├── test_mapper.py
│   │   ├── test_multiformat_endpoint.py
│   │   ├── test_query.py
│   │   ├── test_request.py
│   │   └── test_response.py
│   └── integration/             — Integration tests against live NetBox in Docker.
│       ├── conftest.py          — Docker setup: spin up netbox-docker, wait for ready.
│       ├── test_circuits.py
│       ├── test_dcim.py
│       └── test_ipam.py
├── docs/                        — mkdocs site (API reference + guides).
├── .github/workflows/
│   ├── py3.yml                  — Lint + tests on every push/PR (matrix: Python × NetBox).
│   ├── publish.yml              — PyPI publish on GitHub release.
│   └── build-mkdocs.yml         — Deploy docs to GitHub Pages on push to master.
├── AGENTS.md                    — This file.
├── CLAUDE.md                    — Shim that pulls in this file.
├── CHANGELOG.md                 — Release history.
├── mkdocs.yml                   — Docs site config.
├── requirements.txt             — Runtime dependencies.
├── requirements-dev.txt         — Dev/test dependencies.
└── setup.py                     — Package metadata; version from setuptools_scm.
```

## Architecture

The library follows a layered architecture. Each layer wraps the one below it.

### API Layer (`pynetbox/core/api.py`)

`Api` is the main entry point. On construction it eagerly creates `App` instances for every built-in NetBox application (dcim, ipam, circuits, virtualization, extras, users, wireless, core, vpn, tenancy) plus a `PluginsApp` for plugin endpoints. It owns the `requests.Session`, authentication token, threading flag, and `strict_filters` setting.

### App Layer (`pynetbox/core/app.py`)

`App` represents a NetBox application. Attribute access (`nb.dcim.devices`) is handled by `__getattr__`, which lazily constructs and returns an `Endpoint`. `PluginsApp` adds plugin namespace handling, converting dashes to underscores so `nb.plugins.my_plugin.objects` works.

### Endpoint Layer (`pynetbox/core/endpoint.py`)

`Endpoint` exposes CRUD operations:

| Method | Description |
|---|---|
| `.all()` | Return all objects (paginated, threading-aware). |
| `.filter(**kwargs)` | Return matching objects. |
| `.get(id_or_kwargs)` | Return a single object. |
| `.count(**kwargs)` | Return a count. |
| `.create(data)` | Create one or more objects. |
| `.update(data)` | Bulk-update objects. |
| `.delete(data)` | Bulk-delete objects. |
| `.choices()` | Return field choices from the OPTIONS response. |

Endpoint names are translated from Python attribute style to URL slugs (`ip_addresses` → `ip-addresses`). When `strict_filters=True`, filter kwargs are validated against the OpenAPI spec before the request is sent.

### Query Layer (`pynetbox/core/query.py`)

`Request` handles all HTTP communication. It supports threading for `.all()` and `.filter()` operations (parallel page fetching). Custom exceptions: `RequestError`, `AllocationError`, `ContentError`, `ParameterValidationError`.

### Response Layer (`pynetbox/core/response.py`)

`Record` represents a single API object. Supports attribute access, dict-like access, `.save()` (PATCH), and `.delete()`. `RecordSet` is a lazy iterable returned by `.all()` and `.filter()`; it pages through results on demand.

### Models Module (`pynetbox/models/`)

Custom `Record` subclasses in `pynetbox/models/` add endpoint-specific behaviour:

| File | Content |
|---|---|
| `dcim.py` | `TraceableRecord` (cable tracing), `Cables` (A/B termination serialization), `DetailEndpoints`. |
| `ipam.py` | `IpAddresses`, `Prefixes`, `VLANs` and related types. |
| `circuits.py` | Circuit-specific record types. |
| `virtualization.py` | Virtual machine record types. |
| `extras.py` | Custom fields, tags, webhooks. |
| `users.py` | User and permission record types. |
| `wireless.py` | Wireless endpoint record types. |
| `core.py` | `DataSources`, `Jobs`, `ObjectChanges`. |
| `mapper.py` | `CONTENT_TYPE_MAPPER`: maps NetBox content-type strings (e.g. `"dcim.device"`) to their custom `Record` subclass; used when resolving polymorphic nested objects. |

### Key Design Patterns

- **Lazy endpoint creation**: `Endpoint` objects are constructed on first attribute access via `App.__getattr__`; top-level `App` objects are created eagerly in `Api.__init__`.
- **Threading**: Enable with `threading=True` in `Api()` for parallel page fetching on `.all()` / `.filter()`.
- **Custom sessions**: Replace `api.http_session` with a configured `requests.Session` for custom SSL certs, timeouts, or retry logic.
- **Branch support**: `api.activate_branch(branch_name)` context manager for the NetBox branching plugin.
- **Strict filter validation**: `strict_filters=True` validates filter parameters against the OpenAPI spec before sending requests, raising `ParameterValidationError` for unknown params.

## Commands

| Command | What it does |
|---|---|
| `pip install -r requirements.txt && pip install -r requirements-dev.txt && pip install -e .` | Install all dependencies in editable mode |
| `pytest tests/unit` | Run unit tests only (no Docker required) |
| `pytest tests/integration --netbox-versions 4.5` | Run integration tests against NetBox 4.5 (requires Docker) |
| `pytest --netbox-versions 4.3,4.4,4.5` | Run against multiple NetBox versions |
| `pytest --no-cleanup` | Leave Docker containers running after tests |
| `pytest -p no:docker --url-override http://localhost:8000` | Run integration tests against an existing NetBox instance |
| `ruff check pynetbox/ tests/` | Run linter |
| `ruff check --fix pynetbox/ tests/` | Fix auto-fixable lint issues |
| `mkdocs serve` | Preview docs locally |
| `mkdocs gh-deploy` | Deploy docs to GitHub Pages |
| `python -m build` | Build sdist + wheel (matches the release workflow) |

## Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt -e .
```

Integration tests require Docker. The `tests/integration/conftest.py` uses `pytest-docker` to pull and start `netbox-docker` containers, wait for NetBox to be ready, run the tests, and tear down (unless `--no-cleanup`).

## Testing

- **Unit tests** (`tests/unit/` and `tests/test_*.py`) mock HTTP responses with JSON fixtures from `tests/fixtures/`. No Docker required.
- **Integration tests** (`tests/integration/`) run against a real NetBox instance in Docker. They test end-to-end CRUD operations across dcim, ipam, and circuits.
- `tests/conftest.py` defines three pytest options: `--netbox-versions` (comma-separated, default `4.4`), `--no-cleanup`, and `--url-override`.

| Test module | Coverage area |
|---|---|
| `tests/unit/test_endpoint.py` | Endpoint CRUD method behaviour |
| `tests/unit/test_endpoint_strict_filter.py` | Strict filter parameter validation |
| `tests/unit/test_detailendpoint.py` | DetailEndpoint (objects without list views) |
| `tests/unit/test_response.py` | Record / RecordSet deserialization |
| `tests/unit/test_request.py` | Request HTTP layer |
| `tests/unit/test_query.py` | Query construction |
| `tests/unit/test_extras.py` | Extras model handling |
| `tests/unit/test_mapper.py` | CONTENT_TYPE_MAPPER resolution |
| `tests/unit/test_file_upload.py` | File upload support |
| `tests/unit/test_multiformat_endpoint.py` | Multi-format endpoint responses |
| `tests/test_api.py` | Api class initialization and status |
| `tests/test_app.py` | App / PluginsApp attribute access |
| `tests/test_dcim.py` | DCIM model behavior (older style) |
| `tests/test_circuits.py` | Circuits model behavior (older style) |
| `tests/test_tenancy.py` | Tenancy model behavior |
| `tests/test_users.py` | Users model behavior |
| `tests/test_virtualization.py` | Virtualization model behavior |
| `tests/test_wireless.py` | Wireless model behavior |
| `tests/integration/test_dcim.py` | DCIM end-to-end against live NetBox |
| `tests/integration/test_ipam.py` | IPAM end-to-end against live NetBox |
| `tests/integration/test_circuits.py` | Circuits end-to-end against live NetBox |

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **`py3.yml`** — Runs on every push/PR. Matrix: Python × {3.12, 3.13, 3.14} and NetBox × {4.3, 4.4, 4.5}. Enables Docker IPv6, runs `ruff check`, then `pytest --netbox-versions=${{ matrix.netbox }}` (integration + unit).
- **`publish.yml`** — Runs on published GitHub releases. Builds sdist + wheel with `python -m build`, then publishes to PyPI using a token secret (`PYPI_API_TOKEN`).
- **`build-mkdocs.yml`** — Runs on push to `master`/`main`. Deploys docs to GitHub Pages with `mkdocs gh-deploy --force`.

## Common Tasks

### Add support for a new NetBox endpoint

1. If the endpoint returns objects that need custom behaviour (e.g. nested serialization, tracing), add a `Record` subclass to the appropriate `pynetbox/models/<app>.py`.
2. Register the subclass in `CONTENT_TYPE_MAPPER` in `pynetbox/models/mapper.py` if it can appear as a nested polymorphic object.
3. Add unit tests in `tests/unit/` with fixture JSON in `tests/fixtures/<app>/`.
4. Add integration tests in `tests/integration/test_<app>.py` if appropriate.

### Add or change serialization behavior

Serialization for PATCH/PUT/POST is handled in `Record.serialize()` (`pynetbox/core/response.py`). Nested objects are reduced to IDs; tags and certain list fields are treated as sets. Custom serialization for specific models lives in their `Record` subclass.

### Bump the supported NetBox version

1. Update `DEFAULT_NETBOX_VERSIONS` in `tests/conftest.py` if changing the default test target.
2. Widen the `netbox` matrix in `.github/workflows/py3.yml`.
3. Update the version compatibility table in this file and in `CHANGELOG.md`.
4. Run integration tests locally against the new version.

### Cut a release

1. Ensure all changes are merged to `master`.
2. Tag the commit with the new version (e.g. `git tag v7.8.0`). `setuptools_scm` derives `__version__` from the tag.
3. Publish a GitHub release. `publish.yml` builds and pushes to PyPI automatically.
4. Update `CHANGELOG.md`.

## Conventions and Patterns

- **No Django, no ORM.** pynetbox is a pure Python HTTP client; do not introduce Django or ORM dependencies.
- **`Record` subclasses for model-specific behavior.** Specialised deserialization, computed properties, and serialization overrides belong in `pynetbox/models/<app>.py`, not in the core layer.
- **`CONTENT_TYPE_MAPPER` for polymorphic resolution.** When a nested object's type is determined at runtime (e.g. a cable termination), `mapper.py` maps the NetBox content-type string to the correct `Record` subclass.
- **Underscores to dashes in URL slugs.** `Endpoint.__init__` converts `ip_addresses` → `ip-addresses` automatically; do not hardcode slugs elsewhere.
- **Threading is opt-in.** The default `Api()` is single-threaded. Threading is enabled per-instance with `threading=True`; thread safety is the caller's responsibility beyond that.
- **Commit messages** should be prefixed with `Fixes #NNN:` or `Closes #NNN:` referencing the GitHub issue.
- **Linting**: `ruff check pynetbox/ tests/` must pass before committing.

## Troubleshooting

- **`RequestError` on every call** — Verify the `url` passed to `Api()` includes the scheme (`http://` or `https://`) and no trailing slash issues. Check that the token is valid.
- **`ParameterValidationError` for a valid filter** — Either the filter name is wrong (check the NetBox API docs) or the OpenAPI spec for your NetBox version doesn't list it. Use `strict_filters=False` (the default) to bypass validation, or fix the parameter name.
- **Integration tests hang waiting for Docker** — Docker may not be running or the `netbox-docker` image pull is stalled. Check `docker ps` and Docker daemon logs.
- **Integration tests fail with connection refused** — NetBox health check may have timed out before the instance was ready. Re-run with `--no-cleanup` and inspect the container logs.
- **Stale `.pyc` / import errors after refactoring** — Run `find . -name '*.pyc' -delete` or recreate the venv.

## Version Compatibility

NetBox version compatibility is strict. Defer to `CHANGELOG.md` for the full history.

| pynetbox | NetBox |
|---|---|
| 7.7.0 | 4.3, 4.4, 4.5 |
| 7.6.1 | 4.5.0 |
| 7.5.0 | 4.1, 4.2, 4.3 |
| 7.4.1 | 4.0.6 |
| 7.0.0+ | 3.3+ |

## References

- GitHub repository: <https://github.com/netbox-community/pynetbox>
- PyPI package: <https://pypi.org/project/pynetbox/>
- User docs (mkdocs): [`docs/`](./docs/)
- NetBox REST API docs: <https://demo.netbox.dev/api/docs/>
- Release history: [`CHANGELOG.md`](./CHANGELOG.md)
