# Release Notes

## Version 7.6.0 (January 9, 2026)

### Breaking Changes
- **ObjectChange** moved to `core` module for NetBox 4.1.0+ compatibility
  - Previously located in `extras.object_changes`
  - Now accessible via `nb.core.object_changes`

### New Features
- Support for v2 Tokens introduced in NetBox 4.5.0
- Enhanced token management capabilities

### Enhancements
- Added SVG support for Rack Elevation endpoint
  - Rack elevation diagrams can now be rendered as SVG
  - Access via `rack.elevation.list(render='svg')`

### Bug Fixes
- Fixed token authentication when retrieving NetBox version
  - Prevents 403 errors during version checks
  - Token now properly included in version API requests

### Compatibility
- Supports NetBox 4.5

---

## Version 7.5.0 (May 20, 2024)

### Enhancements
- Expanded cable trace functionality to include:
  - CircuitTerminations
  - ConsolePorts
  - ConsoleServerPorts
  - PowerOutlets
  - PowerPorts
- Added built-in function to activate a branch
  - Use `nb.activate_branch()` context manager for NetBox branching plugin

### Bug Fixes
- Fixed choices returned when API tokens have PUT but not POST permissions
- Fixed `nb.version` property when using OIDC proxy authentication

### Compatibility
- Supports NetBox 4.1, 4.2, 4.3, 4.4

---

## Version 7.4.1 (October 25, 2024)

### Security
- Updated `requests` and `urllib3` Python libraries to address security vulnerabilities
- No functional changes

---

## Version 7.4.0 (August 8, 2024)

### Enhancements
- Added initial NetBox 4.0 support
- Added Python 3.12 support

### Bug Fixes
- Fixed complex custom_fields insertion failures
- Replaced `None` with `'null'` in query parameters
- Corrected connected endpoints behavior

### Testing
- Removed Python 3.8 and 3.9 from test matrix
- Added Python 3.12 to CI/CD pipeline

### Compatibility
- Supports NetBox 4.0.6+

---

## Version 7.3.4 (July 2, 2024)

### Bug Fixes
- Fixed API version detection for NetBox versions exceeding 4.x
- Removed linting errors

### Testing
- Dropped NetBox 3.3 from test matrix
- Focus on NetBox 4.x support

---

## Version 7.3.3 (January 5, 2024)

### Fixes
- PyPI release fix
- No functional changes

---

## Version 7.3.2 (January 4, 2024)

### Fixes
- Fixed setup.py for new publish workflow
- No functional changes

---

## Version 7.3.1 (January 4, 2024)

### Fixes
- Updated PyPI publish workflow
- No functional changes

---

## Version 7.3.0 (January 3, 2024)

### New Features
- Added NetBox v3.7 support

### Dependencies
- Added `pyyaml` dependency

### Testing
- Updated test suite for NetBox 3.7 compatibility

### Compatibility
- Supports NetBox 3.7

---

## Version 7.2.0 (September 7, 2023)

### New Features
- Added NetBox v3.6 support

### Compatibility
- Supports NetBox 3.6

---

## Version 7.1.0 (August 2023)

### Code Quality
- Lint fixes and code cleanup
- Improved code formatting consistency

### Compatibility
- Supports NetBox 3.5

---

## Version 7.0.1 (June 2023)

### Enhancements
- Updated code formatting
- Documentation improvements

---

## Version 7.0.0 (June 2023)

### Breaking Changes
- **Minimum NetBox version**: 3.3+
- Removed support for NetBox versions below 3.3

### New Features
- Full NetBox 3.3 API support
- Updated test suite for NetBox 3.3

### Testing
- Completely overhauled test scripts
- Updated test settings for NetBox 3.3 compatibility
- Improved integration test coverage

### Compatibility
- **NetBox 3.3+ required**
- Python 3.8+ required

---

## Version 6.7.x and Earlier

For release notes for versions 6.7 and earlier, please refer to the [GitHub Releases page](https://github.com/netbox-community/pynetbox/releases).

Key highlights from earlier versions:

### Version 6.7 (Last pre-7.0 release)
- Last version to support NetBox < 3.3
- Python 3.7+ support

### Version 6.6
- Custom error pickling fixes
- VLAN __str__ improvements
- VirtualChassis enhancements

### Version 6.5
- Added available-vlans support for VLAN groups

### Version 6.4
- Added Wireless app support
- Data returned as dict improvements

### Version 6.3
- Field name lookup improvements
- Enhanced filtering capabilities

---

## Upgrade Guide

### Upgrading to 7.x from 6.x

**Important**: Version 7.0+ requires NetBox 3.3 or higher.

If you're running NetBox 3.2 or earlier:
1. First upgrade NetBox to 3.3 or higher
2. Then upgrade pynetbox to 7.0+

```bash
# Check your NetBox version first
import pynetbox
nb = pynetbox.api('http://your-netbox', token='your-token')
print(nb.version)

# If NetBox >= 3.3, upgrade pynetbox
pip install --upgrade pynetbox
```

### Breaking Changes Between Major Versions

#### 7.0 → 7.6
- ObjectChange moved from `extras` to `core` (7.6.0)

#### 6.x → 7.0
- Minimum NetBox version is now 3.3
- Test infrastructure completely redesigned
- Some internal APIs changed (most user-facing APIs unchanged)

---

## Version Compatibility Matrix

| PyNetBox Version | NetBox Version | Python Version | Release Date |
|:----------------:|:--------------:|:--------------:|:------------:|
|      7.6.0       |     4.5        |   3.10-3.12    | Jan 2026    |
|      7.5.0       |   4.1-4.4      |   3.10-3.12    | May 2024    |
|      7.4.1       |     4.0.6      |   3.10-3.12    | Oct 2024    |
|      7.4.0       |     4.0.0      |   3.10-3.12    | Aug 2024    |
|      7.3.4       |     4.0+       |   3.8-3.11     | Jul 2024    |
|      7.3.0       |     3.7        |   3.8-3.11     | Jan 2024    |
|      7.2.0       |     3.6        |   3.8-3.11     | Sep 2023    |
|      7.1.0       |     3.5        |   3.8-3.11     | Aug 2023    |
|      7.0.0       |     3.3        |   3.8-3.11     | Jun 2023    |
|      6.7.x       |   2.11-3.2     |   3.7-3.10     | 2022-2023   |

---

## Contributing

Found a bug or have a feature request? Please open an issue on [GitHub](https://github.com/netbox-community/pynetbox/issues).

Want to contribute code? Pull requests are welcome! Please see our [Development Guide](development/index.md) for more information.
