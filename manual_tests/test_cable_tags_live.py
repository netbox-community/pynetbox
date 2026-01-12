#!/usr/bin/env python
"""Test cable tags with a live NetBox instance"""

import pynetbox

# Connect to local NetBox
nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="adbf699007aa3b231261347cc9b8afde282c1809",
    threading=True,
)

print("Fetching cables...")
try:
    cables = list(nb.dcim.cables.all())
    print(f"Found {len(cables)} cables")

    if cables:
        cable = cables[0]
        print(f"\nFirst cable: {cable}")
        print(f"Cable ID: {cable.id}")
        print(f"Cable tags: {cable.tags}")
        print(f"Tags type: {type(cable.tags)}")

        if cable.tags:
            print(f"First tag: {cable.tags[0]}")
            print(f"First tag type: {type(cable.tags[0])}")
            print(
                f"First tag dict: {dict(cable.tags[0]) if hasattr(cable.tags[0], '__iter__') else 'N/A'}"
            )

        # Try to serialize
        print("\nSerializing cable...")
        serialized = cable.serialize()
        print(f"Serialized tags: {serialized['tags']}")

        # Try to modify tags
        print("\nSetting tags to integer list...")
        original_tags = cable.tags
        cable.tags = [1]  # Assume tag ID 1 exists

        # Try to save
        print("Calling save()...")
        try:
            result = cable.save()
            print(f"Save result: {result}")
            print("SUCCESS!")
        except Exception as e:
            print(f"ERROR during save: {e}")
            import traceback

            traceback.print_exc()

        # Restore original tags
        cable.tags = original_tags

    else:
        print("No cables found in the system")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
