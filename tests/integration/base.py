"""Base test class for integration tests."""

import pytest


@pytest.mark.usefixtures("init")
class BaseIntegrationTest:
    """Base test class for integration tests.

    This class provides common test methods for all NetBox app integration tests.
    Subclasses should set the `app` attribute to the appropriate NetBox app name
    (e.g., "dcim", "ipam", "circuits", etc.).
    """

    app = None  # Should be overridden by subclasses

    def _init_helper(
        self,
        request,
        fixture,
        update_field=None,
        filter_kwargs=None,
        endpoint=None,
        str_repr=None,
    ):
        """Initialize test class attributes.

        Args:
            request: pytest request fixture
            fixture: The fixture object being tested
            update_field: Field name to update during tests (optional)
            filter_kwargs: Kwargs for filtering the endpoint (optional)
            endpoint: The endpoint name (e.g., "sites", "devices")
            str_repr: Expected string representation of the fixture (optional)
        """
        request.cls.endpoint = endpoint
        request.cls.fixture = fixture
        request.cls.update_field = update_field
        request.cls.filter_kwargs = filter_kwargs
        request.cls.str_repr = str_repr

    def test_create(self):
        """Test that the fixture was created successfully."""
        assert self.fixture

    def test_str(self):
        """Test the string representation of the fixture."""
        if self.str_repr:
            test = str(self.fixture)
            assert test == self.str_repr

    def test_update_fixture(self):
        """Test updating a field on the fixture."""
        if self.update_field:
            setattr(self.fixture, self.update_field, "Test Value")
            assert self.fixture.save()

    def test_get_fixture_by_id(self, api):
        """Test retrieving the fixture by ID."""
        test = getattr(getattr(api, self.app), self.endpoint).get(self.fixture.id)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_get_fixture_by_kwarg(self, api):
        """Test retrieving the fixture using keyword arguments."""
        test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_filter_fixture(self, api):
        """Test filtering the endpoint to find the fixture."""
        test = list(
            getattr(getattr(api, self.app), self.endpoint).filter(**self.filter_kwargs)
        )[0]
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"
