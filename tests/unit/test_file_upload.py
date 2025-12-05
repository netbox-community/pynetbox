"""Tests for file upload/multipart support."""

import io
import unittest
from unittest.mock import Mock, patch

from pynetbox.core.query import Request, _extract_files, _is_file_like
from pynetbox.core.endpoint import Endpoint


class TestIsFileLike(unittest.TestCase):
    """Tests for _is_file_like helper function."""

    def test_file_object(self):
        """File objects should be detected as file-like."""
        f = io.BytesIO(b"test content")
        self.assertTrue(_is_file_like(f))

    def test_string_io(self):
        """StringIO objects should be detected as file-like."""
        f = io.StringIO("test content")
        self.assertTrue(_is_file_like(f))

    def test_string(self):
        """Strings should not be detected as file-like."""
        self.assertFalse(_is_file_like("test"))

    def test_bytes(self):
        """Bytes should not be detected as file-like."""
        self.assertFalse(_is_file_like(b"test"))

    def test_dict(self):
        """Dicts should not be detected as file-like."""
        self.assertFalse(_is_file_like({"key": "value"}))

    def test_none(self):
        """None should not be detected as file-like."""
        self.assertFalse(_is_file_like(None))

    def test_non_callable_read_attribute(self):
        """Objects with non-callable read attribute should not be file-like."""

        class FakeFile:
            read = "not a method"

        self.assertFalse(_is_file_like(FakeFile()))


class TestExtractFiles(unittest.TestCase):
    """Tests for _extract_files helper function."""

    def test_no_files(self):
        """Data without files should return unchanged."""
        data = {"name": "test", "device": 1}
        clean_data, files = _extract_files(data)
        self.assertEqual(clean_data, {"name": "test", "device": 1})
        self.assertIsNone(files)

    def test_extract_file_object(self):
        """File objects should be extracted from data."""
        file_obj = io.BytesIO(b"test content")
        data = {"name": "test", "image": file_obj}
        clean_data, files = _extract_files(data)

        self.assertEqual(clean_data, {"name": "test"})
        self.assertIn("image", files)
        self.assertEqual(files["image"][0], "image")  # filename defaults to key
        self.assertEqual(files["image"][1], file_obj)

    def test_extract_file_with_name_attribute(self):
        """File objects with name attribute should use that as filename."""
        file_obj = io.BytesIO(b"test content")
        file_obj.name = "/path/to/image.png"
        data = {"name": "test", "image": file_obj}
        clean_data, files = _extract_files(data)

        self.assertEqual(files["image"][0], "image.png")  # basename extracted

    def test_tuple_format(self):
        """Files passed as tuples should be preserved."""
        file_obj = io.BytesIO(b"test content")
        data = {"name": "test", "image": ("custom_name.png", file_obj, "image/png")}
        clean_data, files = _extract_files(data)

        self.assertEqual(clean_data, {"name": "test"})
        self.assertEqual(files["image"], ("custom_name.png", file_obj, "image/png"))

    def test_non_dict_data(self):
        """Non-dict data should be returned unchanged."""
        data = [{"id": 1}, {"id": 2}]
        result_data, files = _extract_files(data)
        self.assertEqual(result_data, data)
        self.assertIsNone(files)


class TestRequestWithFiles(unittest.TestCase):
    """Tests for Request._make_call with file uploads."""

    def test_post_with_files_uses_multipart(self):
        """POST with files should use multipart/form-data."""
        mock_session = Mock()
        mock_session.post.return_value.ok = True
        mock_session.post.return_value.status_code = 201
        mock_session.post.return_value.json.return_value = {"id": 1, "name": "test"}

        file_obj = io.BytesIO(b"test content")
        req = Request(
            base="http://localhost:8000/api/extras/image-attachments",
            http_session=mock_session,
            token="testtoken",
        )
        req._make_call(
            verb="post",
            data={"object_type": "dcim.device", "object_id": 1, "image": file_obj},
        )

        # Verify multipart was used (data= instead of json=)
        mock_session.post.assert_called_once()
        call_kwargs = mock_session.post.call_args
        self.assertIn("data", call_kwargs.kwargs)
        self.assertIn("files", call_kwargs.kwargs)
        self.assertNotIn("json", call_kwargs.kwargs)

        # Verify Content-Type was not set (requests handles it for multipart)
        headers = call_kwargs.kwargs["headers"]
        self.assertNotIn("Content-Type", headers)
        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["authorization"], "Token testtoken")

    def test_post_without_files_uses_json(self):
        """POST without files should use JSON."""
        mock_session = Mock()
        mock_session.post.return_value.ok = True
        mock_session.post.return_value.status_code = 201
        mock_session.post.return_value.json.return_value = {"id": 1, "name": "test"}

        req = Request(
            base="http://localhost:8000/api/dcim/devices",
            http_session=mock_session,
            token="testtoken",
        )
        req._make_call(verb="post", data={"name": "test-device", "site": 1})

        mock_session.post.assert_called_once()
        call_kwargs = mock_session.post.call_args
        self.assertIn("json", call_kwargs.kwargs)
        self.assertNotIn("files", call_kwargs.kwargs)
        self.assertEqual(
            call_kwargs.kwargs["headers"]["Content-Type"], "application/json"
        )

    def test_patch_with_files_uses_multipart(self):
        """PATCH with files should use multipart/form-data."""
        mock_session = Mock()
        mock_session.patch.return_value.ok = True
        mock_session.patch.return_value.status_code = 200
        mock_session.patch.return_value.json.return_value = {"id": 1, "name": "test"}

        file_obj = io.BytesIO(b"new content")
        req = Request(
            base="http://localhost:8000/api/extras/image-attachments",
            http_session=mock_session,
            token="testtoken",
            key=1,
        )
        req._make_call(verb="patch", data={"image": file_obj})

        mock_session.patch.assert_called_once()
        call_kwargs = mock_session.patch.call_args
        self.assertIn("data", call_kwargs.kwargs)
        self.assertIn("files", call_kwargs.kwargs)

    def test_patch_without_files_uses_json(self):
        """PATCH without files should use JSON and set Content-Type."""
        mock_session = Mock()
        mock_session.patch.return_value.ok = True
        mock_session.patch.return_value.status_code = 200
        mock_session.patch.return_value.json.return_value = {"id": 1, "name": "updated"}

        req = Request(
            base="http://localhost:8000/api/dcim/devices",
            http_session=mock_session,
            token="testtoken",
            key=1,
        )
        req._make_call(verb="patch", data={"name": "updated-device"})

        mock_session.patch.assert_called_once()
        call_kwargs = mock_session.patch.call_args
        self.assertIn("json", call_kwargs.kwargs)
        self.assertNotIn("files", call_kwargs.kwargs)
        self.assertEqual(
            call_kwargs.kwargs["headers"]["Content-Type"], "application/json"
        )


class TestEndpointCreateWithFiles(unittest.TestCase):
    """Tests for Endpoint.create() with file uploads."""

    def test_create_image_attachment(self):
        """Creating image attachment should work with file objects."""
        with patch("pynetbox.core.query.Request._make_call") as mock_call:

            mock_call.return_value = {
                "id": 1,
                "object_type": "dcim.device",
                "object_id": 1,
                "image": "/media/image-attachments/test.png",
                "name": "test.png",
            }

            api = Mock(base_url="http://localhost:8000/api")
            app = Mock(name="extras")
            endpoint = Endpoint(api, app, "image_attachments")

            file_obj = io.BytesIO(b"fake image content")
            endpoint.create(
                object_type="dcim.device", object_id=1, image=file_obj, name="test.png"
            )

            mock_call.assert_called_once()
            call_kwargs = mock_call.call_args
            self.assertEqual(call_kwargs.kwargs["verb"], "post")
            data = call_kwargs.kwargs["data"]
            self.assertEqual(data["object_type"], "dcim.device")
            self.assertEqual(data["object_id"], 1)
            self.assertEqual(data["image"], file_obj)
