#!/usr/bin/env python
"""Integration test for rack elevation SVG rendering (PR #720)"""

import pynetbox
import os
import tempfile

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="60702be68262aa981ab7f821b02fbb46a0833a74",
)

print("=" * 70)
print("Testing Rack Elevation SVG Support (PR #720)")
print("=" * 70)

# Test 1: Get rack with id=1
print("\n[Test 1] Fetching rack with id=1...")
try:
    rack = nb.dcim.racks.get(1)
    print(f"✓ Successfully retrieved rack: {rack.name} (ID: {rack.id})")
    print(
        f"  Facility ID: {rack.facility_id if hasattr(rack, 'facility_id') else 'N/A'}"
    )
    print(f"  U-height: {rack.u_height if hasattr(rack, 'u_height') else 'N/A'}")
except Exception as e:
    print("✗ ERROR: Could not fetch rack with id=1")
    print(f"  {type(e).__name__}: {e}")
    exit(1)

# Test 2: Get elevation as JSON (default behavior)
print("\n[Test 2] Getting rack elevation as JSON (default)...")
try:
    units_json = rack.elevation.list()
    # Convert generator to list to inspect
    units_list = list(units_json)
    print("✓ Successfully retrieved JSON elevation data")
    print(f"  Type: {type(units_list)}")
    print(f"  Number of rack units: {len(units_list)}")

    if units_list:
        first_unit = units_list[0]
        print(f"  First unit type: {type(first_unit)}")
        print(f"  First unit has 'id' attr: {hasattr(first_unit, 'id')}")
        if hasattr(first_unit, "id"):
            print(f"  First unit ID: {first_unit.id}")
        if hasattr(first_unit, "name"):
            print(f"  First unit name: {first_unit.name}")
except Exception as e:
    print("✗ ERROR: Failed to get JSON elevation")
    print(f"  {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

# Test 3: Get elevation as JSON explicitly with render='json'
print("\n[Test 3] Getting rack elevation with render='json' parameter...")
try:
    units_json_explicit = rack.elevation.list(render="json")
    units_list_explicit = list(units_json_explicit)
    print("✓ Successfully retrieved JSON elevation data with render='json'")
    print(f"  Type: {type(units_list_explicit)}")
    print(f"  Number of rack units: {len(units_list_explicit)}")
except Exception as e:
    print("✗ ERROR: Failed to get JSON elevation with render='json'")
    print(f"  {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

# Test 4: Get elevation as SVG
print("\n[Test 4] Getting rack elevation as SVG (render='svg')...")
try:
    svg_content = rack.elevation.list(render="svg")
    print("✓ Successfully retrieved SVG elevation diagram")
    print(f"  Type: {type(svg_content)}")
    print(f"  Is string: {isinstance(svg_content, str)}")
    print(f"  Length: {len(svg_content)} characters")
    print(
        f"  Starts with '<svg': {svg_content.strip().startswith('<svg') if svg_content else False}"
    )
    print(f"  Contains '</svg>': {'</svg>' in svg_content if svg_content else False}")

    # Show first 200 chars
    if svg_content:
        preview = svg_content[:200].replace("\n", " ")
        print(f"  Preview: {preview}...")
except Exception as e:
    print("✗ ERROR: Failed to get SVG elevation")
    print(f"  {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
    svg_content = None

# Test 5: Save SVG to file
if svg_content:
    print("\n[Test 5] Saving SVG to file...")
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            temp_path = f.name
            f.write(svg_content)

        # Verify file was written
        file_size = os.path.getsize(temp_path)
        print("✓ Successfully saved SVG to file")
        print(f"  Path: {temp_path}")
        print(f"  Size: {file_size} bytes")

        # Read back to verify
        with open(temp_path, "r") as f:
            saved_content = f.read()

        if saved_content == svg_content:
            print("  ✓ File content matches original SVG")
        else:
            print("  ✗ WARNING: File content differs from original")

        # Clean up
        os.unlink(temp_path)
        print("  Cleaned up temporary file")

    except Exception as e:
        print("✗ ERROR: Failed to save SVG to file")
        print(f"  {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

# Test 6: Verify SVG response is not processed as Record object
print("\n[Test 6] Verifying SVG is raw string, not Record object...")
try:
    svg_result = rack.elevation.list(render="svg")

    # Should be string, not Record
    is_string = isinstance(svg_result, str)
    has_serialize = hasattr(svg_result, "serialize")
    has_save = hasattr(svg_result, "save")
    has_id_attr = hasattr(svg_result, "id")

    print(f"  Is string: {is_string}")
    print(f"  Has 'serialize' method: {has_serialize}")
    print(f"  Has 'save' method: {has_save}")
    print(f"  Has 'id' attribute: {has_id_attr}")

    if is_string and not has_serialize and not has_save:
        print("✓ SVG correctly returned as raw string")
    else:
        print("✗ WARNING: SVG may be wrapped in Record object")

except Exception as e:
    print("✗ ERROR: Failed verification test")
    print(f"  {type(e).__name__}: {e}")

# Test 7: Test unsupported format error handling
print("\n[Test 7] Testing unsupported format error handling...")
try:
    # Try an unsupported format
    result = rack.elevation.list(render="png")
    print("✗ ERROR: Should have raised ValueError for unsupported format")
    print(f"  Unexpectedly got result: {type(result)}")
except ValueError as e:
    error_msg = str(e)
    if "Unsupported render format" in error_msg and "png" in error_msg:
        print("✓ Correctly raised ValueError for unsupported format")
        print(f"  Error message: {error_msg}")
    else:
        print(f"✗ ValueError raised but with unexpected message: {error_msg}")
except Exception as e:
    print("✗ ERROR: Wrong exception type raised")
    print(f"  Expected ValueError, got {type(e).__name__}: {e}")

# Test 8: Test empty/no parameters defaults to JSON
print("\n[Test 8] Verifying default behavior (no render param) returns JSON...")
try:
    default_result = rack.elevation.list()
    default_list = list(default_result)

    # Should be list of objects, not string
    is_list = isinstance(default_list, list)
    if is_list and len(default_list) > 0:
        first_is_record = hasattr(default_list[0], "id") or hasattr(
            default_list[0], "__dict__"
        )
        print(f"  Returns list: {is_list}")
        print(f"  First item is Record-like: {first_is_record}")

        if first_is_record:
            print("✓ Default behavior correctly returns JSON (Record objects)")
        else:
            print("✗ WARNING: Default returns list but items aren't Record-like")
    else:
        print("✗ WARNING: Default didn't return expected list structure")

except Exception as e:
    print("✗ ERROR: Failed default behavior test")
    print(f"  {type(e).__name__}: {e}")

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("All tests completed. Check results above for any ✗ marks.")
print("\nExpected behavior:")
print("  - rack.elevation.list() → Returns JSON (list of RU objects)")
print("  - rack.elevation.list(render='json') → Returns JSON")
print("  - rack.elevation.list(render='svg') → Returns SVG string")
print("  - rack.elevation.list(render='invalid') → Raises ValueError")
