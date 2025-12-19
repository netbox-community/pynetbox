import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.tenancy

HEADERS = {"accept": "application/json"}


class TenancyTests(Generic.Tests):
    app = "tenancy"


class TenantsTestCase(TenancyTests):
    name = "tenants"


class TenantGroupsTestCase(TenancyTests):
    name = "tenant_groups"


class ContactsTestCase(TenancyTests):
    name = "contacts"


class ContactGroupsTestCase(TenancyTests):
    name = "contact_groups"


class ContactRolesTestCase(TenancyTests):
    name = "contact_roles"


class ContactAssignmentsTestCase(TenancyTests):
    name = "contact_assignments"
