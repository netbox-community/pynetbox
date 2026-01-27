# Release Notes

## Version 7.6.1 (January 28, 2026)

#### Enhancements
- [#726](https://github.com/netbox-community/pynetbox/issues/726) - Use `dict` instead of `OrderedDict` in Record serialization

#### New Features
- [#434](https://github.com/netbox-community/pynetbox/issues/434) - Add cable path tracing support for front ports, rear ports, and virtual circuit terminations

#### Bug Fixes
- [#586](https://github.com/netbox-community/pynetbox/issues/586) - Update internal object state after save operations to prevent attribute reset issues

---

## Version 7.6.0 (January 9, 2026)

#### Breaking Changes
- **ObjectChange** moved to `core` module for NetBox 4.1.0+ compatibility
  - Previously located in `extras.object_changes`
  - Now accessible via `nb.core.object_changes`

#### New Features
- Support for v2 Tokens introduced in NetBox 4.5.0
- Enhanced token management capabilities

#### Enhancements
- Added SVG support for Rack Elevation endpoint
  - Rack elevation diagrams can now be rendered as SVG
  - Access via `rack.elevation.list(render='svg')`

#### Bug Fixes
- Fixed token authentication when retrieving NetBox version
  - Prevents 403 errors during version checks
  - Token now properly included in version API requests

#### Compatibility
- Supports NetBox 4.5

---

## Version 7.5.0 (May 20, 2024)

#### Enhancements
- Expanded cable trace functionality to include:
  - CircuitTerminations
  - ConsolePorts
  - ConsoleServerPorts
  - PowerOutlets
  - PowerPorts
- Added built-in function to activate a branch
  - Use `nb.activate_branch()` context manager for NetBox branching plugin

#### Bug Fixes
- Fixed choices returned when API tokens have PUT but not POST permissions
- Fixed `nb.version` property when using OIDC proxy authentication

#### Compatibility
- Supports NetBox 4.1, 4.2, 4.3, 4.4

---

## Version 7.4.1 (October 25, 2024)

#### Security
- Updated `requests` and `urllib3` Python libraries to address security vulnerabilities
- No functional changes

---

## Version 7.4.0 (August 8, 2024)

#### Enhancements
- Added initial NetBox 4.0 support
- Added Python 3.12 support

#### Bug Fixes
- Fixed complex custom_fields insertion failures
- Replaced `None` with `'null'` in query parameters
- Corrected connected endpoints behavior

#### Testing
- Removed Python 3.8 and 3.9 from test matrix
- Added Python 3.12 to CI/CD pipeline

#### Compatibility
- Supports NetBox 4.0.6+

---

## Version 7.3.4 (July 2, 2024)

#### Bug Fixes
- Fixed API version detection for NetBox versions exceeding 4.x
- Removed linting errors

#### Testing
- Dropped NetBox 3.3 from test matrix
- Focus on NetBox 4.x support

---

## Version 7.3.3 (January 5, 2024)

#### Fixes
- PyPI release fix
- No functional changes

---

## Version 7.3.2 (January 4, 2024)

#### Fixes
- Fixed setup.py for new publish workflow
- No functional changes

---

## Version 7.3.1 (January 4, 2024)

#### Fixes
- Updated PyPI publish workflow
- No functional changes

---

## Version 7.3.0 (January 3, 2024)

#### New Features
- Added NetBox v3.7 support

#### Dependencies
- Added `pyyaml` dependency

#### Testing
- Updated test suite for NetBox 3.7 compatibility

#### Compatibility
- Supports NetBox 3.7

---

## Version 7.2.0 (September 7, 2023)

#### New Features
- Added NetBox v3.6 support

#### Compatibility
- Supports NetBox 3.6

---

## Version 7.1.0 (August 2023)

#### Code Quality
- Lint fixes and code cleanup
- Improved code formatting consistency

#### Compatibility
- Supports NetBox 3.5

---

## Version 7.0.1 (June 2023)

#### Enhancements
- Updated code formatting
- Documentation improvements

---

## Version 7.0.0 (June 2023)

#### Breaking Changes
- **Minimum NetBox version**: 3.3+
- Removed support for NetBox versions below 3.3

#### New Features
- Full NetBox 3.3 API support
- Updated test suite for NetBox 3.3

#### Testing
- Completely overhauled test scripts
- Updated test settings for NetBox 3.3 compatibility
- Improved integration test coverage

#### Compatibility
- **NetBox 3.3+ required**
- Python 3.8+ required

---

## Version 6.7.x and Earlier

For release notes for versions 6.7 and earlier, please refer to the [GitHub Releases page](https://github.com/netbox-community/pynetbox/releases).

Key highlights from earlier versions:

#### Version 6.7 (Last pre-7.0 release)
- Last version to support NetBox < 3.3
- Python 3.7+ support

#### Version 6.6
- Custom error pickling fixes
- VLAN __str__ improvements
- VirtualChassis enhancements

#### Version 6.5
- Added available-vlans support for VLAN groups

#### Version 6.4
- Added Wireless app support
- Data returned as dict improvements

#### Version 6.3
- Field name lookup improvements
- Enhanced filtering capabilities

