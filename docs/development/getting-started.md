# Getting Started

This guide will help you get started with development on pynetbox. It covers setting up your development environment and running tests.

## Development Environment

1. Fork the pynetbox repository on GitHub
2. Clone your fork locally
3. Create a virtual environment and install development dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Running Tests

pynetbox uses pytest for testing. The test suite includes both unit tests and integration tests.

### Unit Tests

To run the unit tests:

```bash
pytest tests/unit
```

### Integration Tests

The integration tests require a running NetBox instance. The test suite uses pytest-docker to spin up NetBox instances in Docker containers.

To run the integration tests:

```bash
pytest tests/integration
```

You can specify which versions of NetBox to test against using the `--netbox-versions` flag:

```bash
pytest tests/integration --netbox-versions 4.2 4.3 4.4
```

### Running Specific Tests

You can run specific test files or test functions:

```bash
# Run a specific test file
pytest tests/unit/test_api.py

# Run a specific test function
pytest tests/unit/test_api.py::test_api_status

# Run tests matching a pattern
pytest -k "test_api"
```

### Test Coverage

To run tests with coverage reporting:

```bash
pytest --cov=pynetbox tests/
```

## Submitting Pull Requests

Once you're happy with your work and have verified that all tests pass, commit your changes and push it upstream to your fork. Always provide descriptive (but not excessively verbose) commit messages. Be sure to prefix your commit message with the word "Fixes" or "Closes" and the relevant issue number (with a hash mark). This tells GitHub to automatically close the referenced issue once the commit has been merged.

```bash
git commit -m "Closes #1234: Add IPv5 support"
git push origin
```

Once your fork has the new commit, submit a pull request to the pynetbox repo to propose the changes. Be sure to provide a detailed accounting of the changes being made and the reasons for doing so.

Once submitted, a maintainer will review your pull request and either merge it or request changes. If changes are needed, you can make them via new commits to your fork: The pull request will update automatically.

!!! warning
    Remember, pull requests are permitted only for **accepted** issues. If an issue you want to work on hasn't been approved by a maintainer yet, it's best to avoid risking your time and effort on a change that might not be accepted. (The one exception to this is trivial changes to the documentation or other non-critical resources.) 