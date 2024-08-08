import unittest
from unittest.mock import patch

import pynetbox

host = "http://localhost:8000"

def_kwargs = {
    "token": "abc123",
}


class AppConfigTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.Request.get",
        return_value={
            "tables": {
                "DeviceTable": {
                    "columns": [
                        "name",
                        "status",
                        "tenant",
                        "tags",
                    ],
                },
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


class PluginAppTestCase(unittest.TestCase):
    @patch(
        "pynetbox.core.query.Request.get",
        return_value=[
            {
                "name": "test_plugin",
                "package": "netbox_test_plugin",
            }
        ],
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
