"""
Manual test for issue #586: Can't reset object attribute to its initial value.

This script tests that after saving an attribute change, you can reset it back
to its original value and the save will succeed (not return False).

Before the fix, this would fail:
1. Change attribute from A to B, save() returns True
2. Change attribute from B back to A, save() returns False (BUG)

After the fix:
1. Change attribute from A to B, save() returns True
2. Change attribute from B back to A, save() returns True (FIXED)
"""

import pynetbox

# Connect to local NetBox instance
nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="nbt_jmEaR2a9bQGn.c9ikyDRw46SMH8JeUrBURGKDuNw8imW15nGkFxoE",
)

print("Testing issue #586: Reset object attribute to initial value\n")
print("=" * 60)

# Get first two interfaces - one to use as bridge, one as test subject
interfaces = []
for i, interface in enumerate(nb.dcim.interfaces.all()):
    interfaces.append(interface)
    if i >= 1:  # Stop after getting 2 interfaces
        break

if len(interfaces) < 2:
    print("ERROR: Need at least 2 interfaces to run this test")
    print("Please create some interfaces in NetBox first")
    exit(1)

br_interface = interfaces[0]
test_interface = interfaces[1]

print(f"Bridge interface: {br_interface} (id={br_interface.id})")
print(f"Test interface: {test_interface} (id={test_interface.id})")
print()

# Store original bridge value
original_bridge = test_interface.bridge
print(f"Original bridge value: {original_bridge}")
print()

# If bridge is already None, set it to br_interface first to have a starting state
if test_interface.bridge is None:
    print("Setup: Bridge is None, setting it to br_interface first")
    test_interface.bridge = br_interface
    test_interface.save()
    print(f"  Setup complete, bridge is now: {test_interface.bridge}")
    print()

# Test 1: Set bridge to None
print("Test 1: Setting bridge to None")
test_interface.bridge = None
result1 = test_interface.save()
print(f"  save() returned: {result1}")
print(f"  Current bridge value: {test_interface.bridge}")
assert result1 is True, "First save should return True"
print("  ✓ PASSED\n")

# Test 2: Set bridge back to a value (the br_interface) - THIS WAS THE BUG!
print("Test 2: Setting bridge back to br_interface (this was the bug!)")
test_interface.bridge = br_interface
result2 = test_interface.save()
print(f"  save() returned: {result2}")
print(f"  Current bridge value: {test_interface.bridge}")
assert result2 is True, "Second save should return True (this was the bug!)"
print("  ✓ PASSED\n")

# Test 3: Set bridge to None again (reset from current value) - ALSO THE BUG!
print("Test 3: Setting bridge back to None (this was also the bug!)")
test_interface.bridge = None
result3 = test_interface.save()
print(f"  save() returned: {result3}")
print(f"  Current bridge value: {test_interface.bridge}")
assert result3 is True, "Third save should return True (this was the bug!)"
print("  ✓ PASSED\n")

# Test 4: Set bridge back to br_interface one more time - STILL THE BUG!
print("Test 4: Setting bridge back to interface again (still the bug!)")
test_interface.bridge = br_interface
result4 = test_interface.save()
print(f"  save() returned: {result4}")
print(f"  Current bridge value: {test_interface.bridge}")
assert result4 is True, "Fourth save should return True (this was the bug!)"
print("  ✓ PASSED\n")

# Cleanup: restore original bridge value
print("Cleanup: Restoring original bridge value")
test_interface.bridge = original_bridge
test_interface.save()
print(f"  Restored bridge to: {test_interface.bridge}")
print()

print("=" * 60)
print("All tests PASSED! Issue #586 is fixed. ✓")
