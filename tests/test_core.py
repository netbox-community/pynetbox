import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.core

HEADERS = {"accept": "application/json"}


class CoreBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "core"


class DataSourcesTestCase(CoreBase):
    name = "data_sources"


class JobsTestCase(CoreBase):
    name = "jobs"


class ObjectTypesTestCase(CoreBase):
    name = "object_types"
