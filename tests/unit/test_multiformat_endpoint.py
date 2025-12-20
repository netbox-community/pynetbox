"""Tests for ROMultiFormatDetailEndpoint."""

import unittest
from unittest.mock import patch

import pynetbox


class ROMultiFormatDetailEndpointTestCase(unittest.TestCase):
    """Test cases for ROMultiFormatDetailEndpoint class."""

    def setUp(self):
        """Set up test fixtures."""
        self.nb = pynetbox.api("http://localhost:8000", token="test-token")

    def test_list_returns_json_by_default(self):
        """list() without render parameter returns JSON data."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=[
                {"id": 1, "name": "U1"},
                {"id": 2, "name": "U2"},
            ],
        ):
            result = rack.elevation.list()
            # Should return generator that yields dict items
            result_list = list(result)
            self.assertEqual(len(result_list), 2)
            # Verify custom_return was applied (RUs objects)
            self.assertTrue(hasattr(result_list[0], "id"))

    def test_list_with_render_svg_returns_raw_string(self):
        """list(render='svg') returns raw SVG string."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=svg_content,
        ):
            result = rack.elevation.list(render="svg")
            # Should return raw string, not wrapped in list
            self.assertIsInstance(result, str)
            self.assertEqual(result, svg_content)
            self.assertIn("<svg", result)

    def test_list_with_render_json_returns_json_data(self):
        """list(render='json') explicitly returns JSON data."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=[
                {"id": 1, "name": "U1"},
                {"id": 2, "name": "U2"},
            ],
        ):
            result = rack.elevation.list(render="json")
            # Should return JSON like default behavior
            result_list = list(result)
            self.assertEqual(len(result_list), 2)
            self.assertTrue(hasattr(result_list[0], "id"))

    def test_svg_response_not_processed_by_custom_return(self):
        """SVG response bypasses custom_return transformation."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        svg_content = "<svg><text>Test</text></svg>"
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value=svg_content,
        ):
            result = rack.elevation.list(render="svg")
            # Result should be raw string, not Record object
            self.assertIsInstance(result, str)
            self.assertFalse(hasattr(result, "id"))
            self.assertFalse(hasattr(result, "serialize"))

    def test_empty_response_with_svg(self):
        """Empty SVG response is handled correctly."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value="",
        ):
            result = rack.elevation.list(render="svg")
            # Should return empty string
            self.assertIsInstance(result, str)
            self.assertEqual(result, "")

    def test_create_raises_not_implemented(self):
        """create() raises NotImplementedError (read-only endpoint)."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        # ROMultiFormatDetailEndpoint should be read-only
        with self.assertRaises(NotImplementedError):
            rack.elevation.create({"data": "test"})

    def test_unsupported_render_format_raises_error(self):
        """Unsupported render format raises ValueError."""
        with patch(
            "pynetbox.core.query.Request._make_call",
            return_value={"id": 123, "name": "Test Rack"},
        ):
            rack = self.nb.dcim.racks.get(123)

        # Unsupported render formats should raise ValueError
        with self.assertRaises(ValueError) as context:
            rack.elevation.list(render="png")

        self.assertIn("Unsupported render format", str(context.exception))
        self.assertIn("png", str(context.exception))
