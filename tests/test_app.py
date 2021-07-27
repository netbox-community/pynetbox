import unittest

import six

import pynetbox

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

host = "http://localhost:8000"

def_kwargs = {
    "token": "abc123",
}


class AppCustomChoicesTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.Request.get",
        return_value={
            "Testfield1": {"TF1_1": 1, "TF1_2": 2},
            "Testfield2": {"TF2_1": 3, "TF2_2": 4},
        },
    )
    def test_custom_choices(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        choices = api.extras.custom_choices()
        self.assertEqual(len(choices), 2)
        self.assertEqual(sorted(choices.keys()), ["Testfield1", "Testfield2"])


class AppConfigTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.Request.get",
        return_value={
            "tables": {
                "DeviceTable": {"columns": ["name", "status", "tenant", "tags",],},
            },
        },
    )
    def test_config(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        config = api.users.config()
        self.assertEqual(sorted(config.keys()), ["tables"])
        self.assertEqual(
            sorted(config["tables"]["DeviceTable"]["columns"]),
            ["name", "status", "tags", "tenant"],
        )


class PluginAppCustomChoicesTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.Request.get",
        return_value={
            "Testfield1": {"TF1_1": 1, "TF1_2": 2},
            "Testfield2": {"TF2_1": 3, "TF2_2": 4},
        },
    )
    def test_custom_choices(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        choices = api.plugins.test_plugin.custom_choices()
        self.assertEqual(len(choices), 2)
        self.assertEqual(sorted(choices.keys()), ["Testfield1", "Testfield2"])

    @patch(
        "pynetbox.core.query.Request.get",
        return_value=[{"name": "test_plugin", "package": "netbox_test_plugin",}],
    )
    def test_installed_plugins(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        plugins = api.plugins.installed_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "test_plugin")

    def test_plugin_app_name(self, *_):
        api = pynetbox.api(host, **def_kwargs)
        test_plugin = api.plugins.test_plugin
        self.assertEqual(test_plugin.name, "plugins/test-plugin")
