"""Tests for the pytest-docker integration."""

import pytest
from packaging import version


def test_netbox_version(netbox_service):
    """Verify the reported version of netbox matches what was requested."""
    reported_version = version.Version(netbox_service["api"].version)

    assert reported_version.major == netbox_service["netbox_version"].major
    assert reported_version.minor == netbox_service["netbox_version"].minor
