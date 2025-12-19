import pynetbox

from .generic import Generic

api = pynetbox.api(
    "http://localhost:8000",
)

nb = api.extras

HEADERS = {"accept": "application/json"}


class ExtrasTests(Generic.Tests):
    app = "extras"


class TagsTestCase(ExtrasTests):
    name = "tags"


class WebhooksTestCase(ExtrasTests):
    name = "webhooks"


class ConfigContextsTestCase(ExtrasTests):
    name = "config_contexts"


class CustomFieldsTestCase(ExtrasTests):
    name = "custom_fields"
