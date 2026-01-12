#!/usr/bin/env python
"""Test cable terminations with NetBox v3.3+ format"""

import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="adbf699007aa3b231261347cc9b8afde282c1809",
    threading=True,
)

print(f"NetBox version: {nb.version}")
print()

# Fetch a cable
print("Fetching cables...")
cables = list(nb.dcim.cables.all())
if cables:
    cable = cables[0]
    print(f"Cable: {cable}")
    print(f"Cable ID: {cable.id}")
    print()

    # Check if it has a_terminations (v3.3+ format)
    print("Checking terminations format...")
    print(f"Has 'a_terminations': {hasattr(cable, 'a_terminations')}")
    print(f"Has 'b_terminations': {hasattr(cable, 'b_terminations')}")
    print(f"Has 'termination_a': {hasattr(cable, 'termination_a')}")
    print(f"Has 'termination_b': {hasattr(cable, 'termination_b')}")
    print()

    if hasattr(cable, "a_terminations"):
        print(f"a_terminations: {cable.a_terminations}")
        print(f"a_terminations type: {type(cable.a_terminations)}")
        if cable.a_terminations:
            print(f"First a_termination: {cable.a_terminations[0]}")
            print(f"First a_termination type: {type(cable.a_terminations[0])}")
            if hasattr(cable.a_terminations[0], "__dict__"):
                print(
                    f"First a_termination __dict__: {cable.a_terminations[0].__dict__}"
                )
        print()

    if hasattr(cable, "b_terminations"):
        print(f"b_terminations: {cable.b_terminations}")
        print(f"b_terminations type: {type(cable.b_terminations)}")
        if cable.b_terminations:
            print(f"First b_termination: {cable.b_terminations[0]}")
            print(f"First b_termination type: {type(cable.b_terminations[0])}")
        print()

    # Test serialization
    print("Testing serialization...")
    try:
        serialized = cable.serialize()
        print("Serialization successful!")
        print(f"Serialized a_terminations: {serialized.get('a_terminations', 'N/A')}")
        print(f"Serialized b_terminations: {serialized.get('b_terminations', 'N/A')}")
    except Exception as e:
        print(f"ERROR during serialization: {e}")
        import traceback

        traceback.print_exc()
    print()

    # Test creating a new cable with v3.3+ format
    print("Testing cable creation with v3.3+ format...")
    interfaces = list(nb.dcim.interfaces.all())
    if len(interfaces) >= 2:
        print(f"Found {len(interfaces)} interfaces")
        print(f"Using interface 1: {interfaces[0]} (ID: {interfaces[0].id})")
        print(f"Using interface 2: {interfaces[1]} (ID: {interfaces[1].id})")

        try:
            new_cable = nb.dcim.cables.create(
                a_terminations=[
                    {"object_type": "dcim.interface", "object_id": interfaces[0].id}
                ],
                b_terminations=[
                    {"object_type": "dcim.interface", "object_id": interfaces[1].id}
                ],
            )
            print(f"Created cable: {new_cable}")
            print(f"New cable ID: {new_cable.id}")
            print()

            # Test update
            print("Testing cable update...")
            new_cable.label = "Test Cable Update"
            result = new_cable.save()
            print(f"Save result: {result}")

            # Test serialization of new cable
            print("Serializing new cable...")
            serialized = new_cable.serialize()
            print(
                f"Serialized a_terminations: {serialized.get('a_terminations', 'N/A')}"
            )

            # Clean up
            print("Deleting test cable...")
            new_cable.delete()
            print("Deleted successfully")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("Not enough interfaces to create a test cable")

else:
    print("No cables found")
