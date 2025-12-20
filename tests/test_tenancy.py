import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.tenancy

HEADERS = {"accept": "application/json"}


class TenancyBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "tenancy"


class TenantsTestCase(TenancyBase):
    name = "tenants"


class TenantGroupsTestCase(TenancyBase):
    name = "tenant_groups"


class ContactsTestCase(TenancyBase):
    name = "contacts"


class ContactGroupsTestCase(TenancyBase):
    name = "contact_groups"


class ContactRolesTestCase(TenancyBase):
    name = "contact_roles"


class ContactAssignmentsTestCase(TenancyBase):
    name = "contact_assignments"
