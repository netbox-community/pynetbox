# Release Checklist

This document outlines the steps required to prepare and publish a new release of pynetbox.

## Pre-Release Tasks

1. Ensure all tests are passing:
   ```bash
   pytest
   ```

2. Update version number in `pynetbox/__init__.py`
3. Update documentation for any new features or changes
4. Check NetBox Docker releases:
    - Visit https://github.com/netbox-community/netbox-docker/releases
    - Review the latest NetBox Docker releases and their corresponding NetBox versions
    - Update supported NetBox versions in `tests/integration/conftest.py` if needed
    - Ensure the `get_netbox_docker_version_tag` function in `tests/integration/conftest.py` is updated with any new version mappings

## Release Tasks

1. Create a new release branch from `master`:
   ```bash
   git checkout master
   git pull
   git checkout -b release/vX.Y.Z
   ```

2. Commit version and changelog updates:
   ```bash
   git commit -m "Prepare release vX.Y.Z"
   ```

3. Create a pull request to merge the release branch into `master`

4. Once merged, use github to create a new release:
    1. Go to the GitHub repository
    2. Click "Releases" in the right sidebar
    3. Click "Create a new release"
    4. Create a new tag (e.g., vX.Y.Z)
    5. Use the changelog content as the release description
    6. Publish the release

    The GitHub release will automatically trigger the workflow to publish to PyPI.

## Supported NetBox Versions

pynetbox aims to support the current and previous two minor versions of NetBox. The supported versions are defined in `tests/integration/conftest.py` and should be updated as part of the release process. 