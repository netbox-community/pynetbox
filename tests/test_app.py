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
