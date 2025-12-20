import pytest

from .base import BaseIntegrationTest


class BaseTest(BaseIntegrationTest):
    app = "tenancy"


@pytest.fixture(scope="module")
def tenant_group(api):
    ret = api.tenancy.tenant_groups.create(
        name="test-tenant-group", slug="test-tenant-group"
    )
    yield ret
    ret.delete()


class TestTenantGroup(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, tenant_group):
        self._init_helper(
            request,
            tenant_group,
            filter_kwargs={"name": "test-tenant-group"},
            update_field="description",
            endpoint="tenant_groups",
        )


class TestTenant(BaseTest):
    @pytest.fixture(scope="class")
    def tenant(self, api, tenant_group):
        ret = api.tenancy.tenants.create(
            name="test-tenant", slug="test-tenant", group=tenant_group.id
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, tenant):
        self._init_helper(
            request,
            tenant,
            filter_kwargs={"name": "test-tenant"},
            update_field="description",
            endpoint="tenants",
        )


class TestContactRole(BaseTest):
    @pytest.fixture(scope="class")
    def contact_role(self, api):
        ret = api.tenancy.contact_roles.create(
            name="test-contact-role", slug="test-contact-role"
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, contact_role):
        self._init_helper(
            request,
            contact_role,
            filter_kwargs={"name": "test-contact-role"},
            update_field="description",
            endpoint="contact_roles",
        )


class TestContact(BaseTest):
    @pytest.fixture(scope="class")
    def contact(self, api):
        ret = api.tenancy.contacts.create(name="test-contact")
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, contact):
        self._init_helper(
            request,
            contact,
            filter_kwargs={"name": "test-contact"},
            update_field="comments",
            endpoint="contacts",
        )
