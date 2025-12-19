import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.core

HEADERS = {"accept": "application/json"}


class CoreTests(Generic.Tests):
    app = "core"


class DataSourcesTestCase(CoreTests):
    name = "data_sources"


class JobsTestCase(CoreTests):
    name = "jobs"


class ObjectTypesTestCase(CoreTests):
    name = "object_types"
