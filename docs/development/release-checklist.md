# Release Checklist

This page outlines the steps to prepare and publish a new pynetbox release. The package version is derived from the git tag at release time by [setuptools_scm](https://github.com/pypa/setuptools_scm), so the source tree does not carry a hardcoded version in `setup.py`.

## Pre-Release Tasks

1. Ensure all tests pass:
   ```bash
   ruff check pynetbox/ tests/
   pytest
   ```

2. Update `__version__` in `pynetbox/__init__.py` to the new version.

3. Update [`CHANGELOG.md`](https://github.com/netbox-community/pynetbox/blob/master/CHANGELOG.md) and `docs/release-notes.md` with a summary of changes, referencing the relevant issue and PR numbers.

4. Check supported NetBox versions:
    - Review the latest [netbox-docker releases](https://github.com/netbox-community/netbox-docker/releases).
    - Update `DEFAULT_NETBOX_VERSIONS` and the `get_netbox_docker_version_tag` function in `tests/integration/conftest.py` if there are new NetBox versions or new netbox-docker tag mappings.
    - Widen the `netbox` matrix in `.github/workflows/py3.yml` to cover the supported range.

## Release Tasks

1. Create a release branch from `master`:
   ```bash
   git checkout master
   git pull
   git checkout -b release/vX.Y.Z
   ```

2. Commit the version bump and changelog updates:
   ```bash
   git commit -m "Prepare release vX.Y.Z"
   ```

3. Open a pull request to merge the release branch into `master`.

4. Once the PR is merged, publish a GitHub release:
    1. Go to the [Releases page](https://github.com/netbox-community/pynetbox/releases) on GitHub.
    2. Click **Draft a new release**.
    3. Create a new tag named `vX.Y.Z` against `master`.
    4. Paste the relevant changelog section into the release notes.
    5. Publish the release.

   Publishing triggers the [`publish.yml`](https://github.com/netbox-community/pynetbox/blob/master/.github/workflows/publish.yml) workflow, which builds the sdist and wheel and uploads them to PyPI.

## Supported NetBox Versions

pynetbox aims to support the current and previous two minor versions of NetBox. The supported versions are defined in `tests/integration/conftest.py` and should be reviewed and updated each release cycle.
