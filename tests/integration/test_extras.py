import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "extras"


class TestTag(BaseTest):
    @pytest.fixture(scope="class")
    def tag(self, api):
        ret = api.extras.tags.create(name="test-tag", slug="test-tag")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, tag):
        self._init_helper(
            request,
            tag,
            filter_kwargs={"name": "test-tag"},
            update_field="description",
            endpoint="tags",
        )


class TestConfigContext(BaseTest):
    @pytest.fixture(scope="class")
    def config_context(self, api):
        ret = api.extras.config_contexts.create(
            name="test-context",
            data={"test_key": "test_value"},
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, config_context):
        self._init_helper(
            request,
            config_context,
            filter_kwargs={"name": "test-context"},
            update_field="description",
            endpoint="config_contexts",
        )


class TestCustomField(BaseTest):
    @pytest.fixture(scope="class")
    def custom_field(self, api):
        ret = api.extras.custom_fields.create(
            name="test_custom_field",
            type="text",
            object_types=["dcim.site"],
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, custom_field):
        self._init_helper(
            request,
            custom_field,
            filter_kwargs={"name": "test_custom_field"},
            update_field="description",
            endpoint="custom_fields",
        )


class TestSavedFilter(BaseTest):
    @pytest.fixture(scope="class")
    def saved_filter(self, api):
        ret = api.extras.saved_filters.create(
            name="test-filter",
            slug="test-filter",
            object_types=["dcim.site"],
            parameters={"status": "active"},
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, saved_filter):
        self._init_helper(
            request,
            saved_filter,
            filter_kwargs={"name": "test-filter"},
            update_field="description",
            endpoint="saved_filters",
        )
