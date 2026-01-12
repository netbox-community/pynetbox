#!/usr/bin/env python
"""Test cable creation and updates with terminations"""

import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="adbf699007aa3b231261347cc9b8afde282c1809",
    threading=True,
)

print(f"NetBox version: {nb.version}")
print()

# Find interfaces without cables
print("Finding interfaces without cables...")
interfaces = nb.dcim.interfaces.filter(cabled=False)
interface_list = list(interfaces)[:10]  # Get first 10
print(f"Found {len(interface_list)} uncabled interfaces")

if len(interface_list) >= 2:
    int1, int2 = interface_list[0], interface_list[1]
    print(f"Interface 1: {int1} (ID: {int1.id})")
    print(f"Interface 2: {int2} (ID: {int2.id})")
    print()

    # Create cable with v3.3+ format
    print("Creating cable with a_terminations/b_terminations format...")
    try:
        cable = nb.dcim.cables.create(
            a_terminations=[{"object_type": "dcim.interface", "object_id": int1.id}],
            b_terminations=[{"object_type": "dcim.interface", "object_id": int2.id}],
            label="Test Cable",
        )
        print(f"✓ Created cable: {cable} (ID: {cable.id})")
        print()

        # Test serialization
        print("Serializing cable...")
        serialized = cable.serialize()
        print(f"✓ Serialized a_terminations: {serialized['a_terminations']}")
        print(f"✓ Serialized b_terminations: {serialized['b_terminations']}")
        print()

        # Test update
        print("Testing cable update...")
        cable.label = "Updated Test Cable"
        result = cable.save()
        print(f"✓ Update result: {result}")
        print()

        # Test adding tags
        print("Testing adding tags...")
        tags = list(nb.extras.tags.all())
        if tags:
            cable.tags = [tags[0].id]
            result = cable.save()
            print(f"✓ Tags added, save result: {result}")

            # Re-fetch to see tags
            cable = nb.dcim.cables.get(cable.id)
            print(f"✓ Cable tags after save: {cable.tags}")
        print()

        # Clean up
        print("Cleaning up...")
        cable.delete()
        print("✓ Test cable deleted")

        print("\n✅ ALL TESTS PASSED!")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()

else:
    print("❌ Not enough uncabled interfaces to test")
