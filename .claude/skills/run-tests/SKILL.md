---
name: run-tests
description: Run the pynetbox test suite — unit tests only, integration tests against a live NetBox in Docker, or both. Covers how to pick the right command, pass options, and interpret failures.
version: 1
---

# run-tests

Run the pynetbox test suite. Choose the scope that fits your situation.

## Quick reference

| Goal | Command |
|---|---|
| Unit tests only (no Docker) | `pytest tests/unit` |
| Older-style unit tests only | `pytest tests/test_*.py` |
| All unit tests | `pytest tests/unit tests/test_*.py` |
| Integration tests — default NetBox version (4.4) | `pytest tests/integration --netbox-versions 4.4` |
| Integration tests — specific version | `pytest tests/integration --netbox-versions 4.5` |
| Integration tests — multiple versions | `pytest --netbox-versions 4.3,4.4,4.5` |
| Against an existing NetBox instance | `pytest tests/integration -p no:docker --url-override http://localhost:8000` |
| Leave Docker containers running after tests | `pytest tests/integration --netbox-versions 4.5 --no-cleanup` |
| Lint only | `ruff check pynetbox/ tests/` |
| Lint + auto-fix | `ruff check --fix pynetbox/ tests/` |

## Before running

Activate the virtualenv and confirm dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt -e .
```

Integration tests require Docker. Confirm the daemon is running (`docker ps`) before invoking them.

## Unit tests

Unit tests mock all HTTP responses using JSON fixtures in `tests/fixtures/`. No network access or Docker is needed.

```bash
pytest tests/unit tests/test_*.py
```

Useful flags:
- `-x` — stop on first failure
- `-k <pattern>` — run only tests whose name matches the pattern
- `-v` — verbose output

## Integration tests

Integration tests spin up a `netbox-docker` container, wait for NetBox to be ready, run end-to-end CRUD operations, and tear down the container on exit.

```bash
pytest tests/integration --netbox-versions 4.5
```

- `--netbox-versions` accepts a comma-separated list (`4.3,4.4,4.5`).
- Default version when the flag is omitted: **4.4**.
- `--no-cleanup` leaves the container running — useful for inspecting state after a failure.
- `-p no:docker --url-override http://localhost:8000` skips Docker and targets an existing instance.

## Lint

`ruff` is the project linter. CI enforces `ruff check pynetbox/ tests/` on every push.

```bash
ruff check pynetbox/ tests/          # check only
ruff check --fix pynetbox/ tests/    # auto-fix safe issues
```

Always run the linter before committing; CI will reject lint failures.

## CI matrix

The GitHub Actions workflow (`py3.yml`) runs the full matrix:

- Python versions: 3.12, 3.13, 3.14
- NetBox versions: 4.3, 4.4, 4.5

Reproducing a specific cell locally:

```bash
# Example: Python 3.12 + NetBox 4.3
python3.12 -m pytest tests/ --netbox-versions 4.3
```

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Integration tests hang waiting for Docker | Docker not running or image pull stalled | `docker ps`; check daemon logs |
| `connection refused` on integration tests | NetBox health check timed out before ready | Re-run; use `--no-cleanup` and inspect container logs |
| `ParameterValidationError` in unit tests | Filter param name wrong or fixture out of date | Check the fixture JSON and the parameter name |
| Stale `.pyc` / import errors | Bytecode cache out of sync after refactor | `find . -name '*.pyc' -delete` or recreate the venv |
| Lint failure on CI but not locally | Different `ruff` version | Pin matches `requirements-dev.txt`; run `pip install -r requirements-dev.txt` |
