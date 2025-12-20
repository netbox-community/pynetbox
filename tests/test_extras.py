import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.extras

HEADERS = {"accept": "application/json"}


class ExtrasBase(Generic.Tests):
    __test__ = False  # Prevent pytest from discovering this as a test class
    app = "extras"


class TagsTestCase(ExtrasBase):
    name = "tags"


class WebhooksTestCase(ExtrasBase):
    name = "webhooks"


class ConfigContextsTestCase(ExtrasBase):
    name = "config_contexts"


class CustomFieldsTestCase(ExtrasBase):
    name = "custom_fields"
