import pytest


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "tenancy"

    def _init_helper(
        self,
        request,
        fixture,
        update_field=None,
        filter_kwargs=None,
        endpoint=None,
        str_repr=None,
    ):
        request.cls.endpoint = endpoint
        request.cls.fixture = fixture
        request.cls.update_field = update_field
        request.cls.filter_kwargs = filter_kwargs
        request.cls.str_repr = str_repr

    def test_create(self):
        assert self.fixture

    def test_str(self):
        if self.str_repr:
            test = str(self.fixture)
            assert test == self.str_repr

    def test_update_fixture(self):
        if self.update_field:
            setattr(self.fixture, self.update_field, "Test Value")
            assert self.fixture.save()

    def test_get_fixture_by_id(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(self.fixture.id)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_get_fixture_by_kwarg(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_filter_fixture(self, api):
        test = list(
            getattr(getattr(api, self.app), self.endpoint).filter(**self.filter_kwargs)
        )[0]
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"


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
