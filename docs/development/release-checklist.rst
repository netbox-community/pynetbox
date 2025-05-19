Release Checklist
===============

This document outlines the steps required to prepare and publish a new release of pynetbox.

Pre-Release Tasks
---------------

1. Ensure all tests are passing:

   .. code-block:: bash

       pytest tests/

2. Verify compatibility with supported NetBox versions:

   .. code-block:: bash

       pytest tests/integration --netbox-versions 4.1 4.2 4.3

3. Update version number in `pynetbox/__init__.py`
4. Update `CHANGELOG.md` with all changes since the last release
5. Update documentation for any new features or changes
6. Review and update supported NetBox versions in `tests/integration/conftest.py`

Release Tasks
-----------

1. Create a new release branch from `main`:

   .. code-block:: bash

       git checkout main
       git pull
       git checkout -b release/vX.Y.Z

2. Commit version and changelog updates:

   .. code-block:: bash

       git add pynetbox/__init__.py CHANGELOG.md
       git commit -m "Prepare release vX.Y.Z"

3. Create a pull request to merge the release branch into `main`
4. Once merged, tag the release:

   .. code-block:: bash

       git tag -a vX.Y.Z -m "Release vX.Y.Z"
       git push origin vX.Y.Z

5. Build and publish the package to PyPI:

   .. code-block:: bash

       python -m build
       python -m twine upload dist/*

Post-Release Tasks
---------------

1. Update the `feature` branch with changes from `main`:

   .. code-block:: bash

       git checkout feature
       git merge main
       git push origin feature

2. Announce the release:
   - Create a GitHub release with release notes
   - Post announcement to GitHub discussions
   - Update any relevant documentation

3. Monitor for any immediate issues or bugs
4. Begin work on the next release cycle

Version Numbering
--------------

pynetbox follows semantic versioning (MAJOR.MINOR.PATCH):

* MAJOR version for incompatible API changes
* MINOR version for backwards-compatible functionality
* PATCH version for backwards-compatible bug fixes

When to Increment
~~~~~~~~~~~~~~~

* MAJOR: Breaking changes to the API or major architectural changes
* MINOR: New features that don't break existing functionality
* PATCH: Bug fixes and minor improvements

Supported NetBox Versions
----------------------

pynetbox aims to support the current and previous two minor versions of NetBox. The supported versions are defined in `tests/integration/conftest.py` and should be updated as part of the release process. 