# Getting Started

This guide walks through setting up a pynetbox development environment and running the test suite.

## Development Environment

1. Fork the pynetbox repository on GitHub.
2. Clone your fork locally.
3. Create a virtual environment and install the runtime and development dependencies:

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

## Running Tests

pynetbox uses [pytest](https://docs.pytest.org/) for both unit tests and integration tests. Linting is handled with [ruff](https://docs.astral.sh/ruff/).

Before submitting changes, make sure `ruff check` passes:

```bash
ruff check pynetbox/ tests/
```

### Unit Tests

Unit tests mock HTTP responses with JSON fixtures from `tests/fixtures/` and have no external dependencies:

```bash
pytest tests/unit
```

### Integration Tests

Integration tests run against real NetBox instances. The suite uses [pytest-docker](https://pypi.org/project/pytest-docker/) to spin up [netbox-docker](https://github.com/netbox-community/netbox-docker) containers, so Docker must be installed and running.

```bash
pytest tests/integration
```

You can choose which NetBox versions to test against with `--netbox-versions` (comma-separated):

```bash
pytest tests/integration --netbox-versions 4.3,4.4,4.5
```

To leave the containers running after the tests finish (useful for debugging):

```bash
pytest tests/integration --no-cleanup
```

To run integration tests against an existing NetBox instance instead of starting containers:

```bash
pytest tests/integration -p no:docker --url-override http://localhost:8000
```

### Running Specific Tests

```bash
# A specific test file
pytest tests/unit/test_endpoint.py

# A specific test function
pytest tests/unit/test_endpoint.py::TestEndpoint::test_get_by_id

# All tests whose name matches a pattern
pytest -k "filter"
```

### Test Coverage

```bash
pytest --cov=pynetbox tests/
```

## Submitting Pull Requests

Once your changes are complete and all tests pass, commit them and push to your fork. Use descriptive commit messages that explain the *why* rather than the *what*. Prefix the subject line with `Fixes #NNN:` or `Closes #NNN:` referencing the relevant issue so that GitHub automatically closes it when the commit merges:

```bash
git commit -m "Closes #1234: Add IPv5 support"
git push origin
```

Open a pull request against the pynetbox repository describing what changed and why. A maintainer will review the PR and either merge it or request changes. You can address review feedback by pushing additional commits to your branch — the pull request updates automatically.

!!! warning
    Pull requests are only accepted for **approved** issues. If the issue you're working on hasn't been triaged and approved by a maintainer yet, please hold off — there's no guarantee it will be accepted. (The one exception is trivial documentation fixes and similar non-critical changes.)
