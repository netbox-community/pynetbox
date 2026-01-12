#!/usr/bin/env python
"""Test to reproduce issue #502 - Save of cable tags not working"""

from pynetbox.core.response import Record

# Simulate a cable object with tags as returned from API
# Tags could come back as dicts with id and name
cable_values = {
    "id": 123,
    "label": "Test Cable",
    "tags": [
        {"id": 1, "name": "tag1"},
        {"id": 2, "name": "tag2"},
    ],
}

print("Test 1: Tags as dicts from API")
cable = Record(cable_values, None, None)
print(f"Cable tags: {cable.tags}")
print(f"Type of first tag: {type(cable.tags[0])}")

# Try to serialize
serialized = cable.serialize()
print(f"Serialized tags: {serialized['tags']}")
print()

# Now simulate setting tags to integer IDs
print("Test 2: Setting tags to integer IDs")
cable.tags = [11]
print(f"Cable tags after setting: {cable.tags}")
print(f"Type of first tag: {type(cable.tags[0])}")

# Try to serialize - this is where the error should occur
try:
    serialized = cable.serialize()
    print(f"Serialized tags: {serialized['tags']}")
    print("SUCCESS: No error!")
except AttributeError as e:
    print(f"ERROR: {e}")
print()

# Test 3: Tags as integers from the start
print("Test 3: Tags as integers from API")
cable_values2 = {"id": 124, "label": "Test Cable 2", "tags": [11, 22]}
cable2 = Record(cable_values2, None, None)
print(f"Cable2 tags: {cable2.tags}")

try:
    serialized2 = cable2.serialize()
    print(f"Serialized tags: {serialized2['tags']}")
    print("SUCCESS: No error!")
except AttributeError as e:
    print(f"ERROR: {e}")
print()

# Test 4: Simulate saving (which calls _diff and serialize)
print("Test 4: Simulating save operation (with _diff)")
cable_values3 = {
    "id": 125,
    "label": "Test Cable 3",
    "tags": [
        {"id": 1, "name": "tag1"},
        {"id": 2, "name": "tag2"},
    ],
}
cable3 = Record(cable_values3, None, None)
cable3.tags = [11]  # Change tags to integer IDs

try:
    diff = cable3._diff()
    print(f"Diff: {diff}")
    updates = cable3.updates()
    print(f"Updates: {updates}")
    print("SUCCESS: No error!")
except AttributeError as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
