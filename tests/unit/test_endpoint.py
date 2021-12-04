import unittest

import six

from pynetbox.core.endpoint import Endpoint

if six.PY3:
    from unittest.mock import patch, Mock, call
else:
    from mock import patch, Mock, call


class EndPointTestCase(unittest.TestCase):
    def test_filter(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            mock.return_value = [{"id": 123}, {"id": 321}]
            test_obj = Endpoint(api, app, "test")
            test = test_obj.filter(test="test")
            self.assertEqual(len(test), 2)

    def test_filter_invalid_pagination_args(self):

        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="test")
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ValueError) as _:
            test_obj.filter(offset=1)

    def test_all_invalid_pagination_args(self):

        api = Mock(base_url="http://localhost:8000/api")
        app = Mock(name="test")
        test_obj = Endpoint(api, app, "test")
        with self.assertRaises(ValueError) as _:
            test_obj.all(offset=1)

    def test_choices(self):
        with patch("pynetbox.core.query.Request.options", return_value=Mock()) as mock:
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            mock.return_value = {
                "actions": {
                    "POST": {
                        "letter": {
                            "choices": [
                                {"display_name": "A", "value": 1},
                                {"display_name": "B", "value": 2},
                                {"display_name": "C", "value": 3},
                            ]
                        }
                    }
                }
            }
            test_obj = Endpoint(api, app, "test")
            choices = test_obj.choices()
            self.assertEqual(choices["letter"][1]["display_name"], "B")
            self.assertEqual(choices["letter"][1]["value"], 2)

    def test_get_with_filter(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            mock.return_value = [{"id": 123}]
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            test = test_obj.get(name="test")
            self.assertEqual(test.id, 123)

    def test_delete_with_ids(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            ids = [1, 3, 5]
            mock.return_value = True
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            test = test_obj.delete(ids)
            mock.assert_called_with(verb="delete", data=[{"id": i} for i in ids])
            self.assertTrue(test)

    def test_delete_with_objects(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            from pynetbox.core.response import Record

            ids = [1, 3, 5]
            mock.return_value = True
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            objects = [
                Record({"id": i, "name": "dummy" + str(i)}, api, test_obj) for i in ids
            ]
            test = test_obj.delete(objects)
            mock.assert_called_with(verb="delete", data=[{"id": i} for i in ids])
            self.assertTrue(test)

    def test_delete_with_recordset(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            from pynetbox.core.response import RecordSet

            ids = [1, 3, 5]

            class FakeRequest:
                def get(self):
                    return iter([{"id": i, "name": "dummy" + str(i)} for i in ids])

            mock.return_value = True
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            recordset = RecordSet(test_obj, FakeRequest())
            test = test_obj.delete(recordset)
            mock.assert_called_with(verb="delete", data=[{"id": i} for i in ids])
            self.assertTrue(test)

    def test_get_greater_than_one(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            mock.return_value = [{"id": 123}, {"id": 321}]
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            with self.assertRaises(ValueError) as _:
                test_obj.get(name="test")

    def test_get_no_results(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            mock.return_value = []
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            test = test_obj.get(name="test")
            self.assertIsNone(test)

    def test_bulk_update_records(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            from pynetbox.core.response import Record

            ids = [1, 3, 5]
            mock.return_value = True
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            test_obj = Endpoint(api, app, "test")
            objects = [
                Record(
                    {"id": i, "name": "dummy" + str(i), "unchanged": "yes"},
                    api,
                    test_obj,
                )
                for i in ids
            ]
            for o in objects:
                o.name = "fluffy" + str(o.id)
            mock.return_value = [o.serialize() for o in objects]
            test = test_obj.update(objects)
            mock.assert_called_with(
                verb="patch", data=[{"id": i, "name": "fluffy" + str(i)} for i in ids]
            )
            self.assertTrue(test)

    def test_bulk_update_json(self):
        with patch(
            "pynetbox.core.query.Request._make_call", return_value=Mock()
        ) as mock:
            ids = [1, 3, 5]
            changes = [{"id": i, "name": "puffy" + str(i)} for i in ids]
            mock.return_value = True
            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="test")
            mock.return_value = changes
            test_obj = Endpoint(api, app, "test")
            test = test_obj.update(changes)
            mock.assert_called_with(verb="patch", data=changes)
            self.assertTrue(test)
