#!/usr/bin/env python
"""Find and test cables with tags"""

import pynetbox

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="60702be68262aa981ab7f821b02fbb46a0833a74",
    threading=True,
)

# First, get all tags to see what's available
print("Fetching tags...")
tags = list(nb.extras.tags.all())
print(f"Found {len(tags)} tags")
if tags:
    for tag in tags[:5]:
        print(f"  Tag ID {tag.id}: {tag.name}")

# Find cables with tags
print("\nFetching cables...")
cables = list(nb.dcim.cables.all())
print(f"Found {len(cables)} cables")

cables_with_tags = [c for c in cables if c.tags]
print(f"Cables with tags: {len(cables_with_tags)}")

if cables_with_tags:
    cable = cables_with_tags[0]
    print(f"\nCable with tags: {cable}")
    print(f"Cable ID: {cable.id}")
    print(f"Tags: {cable.tags}")
    print(f"Tags type: {type(cable.tags)}")

    if cable.tags:
        print(f"First tag: {cable.tags[0]}")
        print(f"First tag type: {type(cable.tags[0])}")
        if hasattr(cable.tags[0], "__dict__"):
            print(f"First tag __dict__: {cable.tags[0].__dict__}")
        if hasattr(cable.tags[0], "id"):
            print(f"First tag id: {cable.tags[0].id}")

    # Test serialization
    print("\nTesting serialization...")
    try:
        serialized = cable.serialize()
        print("Serialized successfully!")
        print(f"Serialized tags: {serialized['tags']}")
    except Exception as e:
        print(f"ERROR during serialization: {e}")
        import traceback

        traceback.print_exc()

    # Test setting tags to integers
    print("\nSetting tags to integer list...")
    original_tags = cable.tags
    cable.tags = [tags[0].id if tags else 1]

    try:
        serialized = cable.serialize()
        print(f"Serialized after setting int tags: {serialized['tags']}")

        print("Calling save()...")
        result = cable.save()
        print(f"Save result: {result}")
        print("SUCCESS!")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Restore original tags
        cable.tags = original_tags
        cable.save()

else:
    # Use an existing cable to test
    print("\nNo cables with tags found. Using an existing cable to test...")

    if not tags:
        print("Creating a test tag first...")
        tag = nb.extras.tags.create(name="test-tag", slug="test-tag")
        print(f"Created tag: {tag} (ID: {tag.id})")
    else:
        tag = tags[0]

    if not cables:
        print("ERROR: No cables available for testing!")
        exit(1)

    # Use the first available cable
    cable = cables[0]
    print(f"\nUsing existing cable: {cable} (ID: {cable.id})")
    original_tags = cable.tags
    print(f"Original tags: {original_tags}")

    # Test the issue - THIS IS THE ACTUAL BUG FROM ISSUE #502
    print("\n" + "=" * 60)
    print("TESTING ISSUE #502: Setting tags to list of integers")
    print("=" * 60)

    print(f"\nSetting cable.tags = [{tag.id}]")
    cable.tags = [tag.id]
    print(f"cable.tags is now: {cable.tags}")

    try:
        print("\nCalling cable.save()...")
        result = cable.save()
        print(f"Save result: {result}")
        print("\n*** SUCCESS! Issue #502 appears to be fixed! ***")
    except AttributeError as e:
        print("\n*** ISSUE #502 REPRODUCED! ***")
        print(f"AttributeError: {e}")
        import traceback

        traceback.print_exc()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Restore original tags
        cable.tags = original_tags
        try:
            cable.save()
            print(f"\nRestored original tags to: {original_tags}")
        except Exception:
            pass

    exit(0)

    # Old code for creating new cables - keeping just in case
    interfaces_old_code = """
    print("\nNote: To test this fully, we need a cable to work with.")
    print("Looking for interfaces not already connected to cables...")

    # Find interfaces that are not connected to a cable
    interfaces = list(nb.dcim.interfaces.filter(cable_id__empty=True))
    if len(interfaces) >= 2:
        print(f"Found {len(interfaces)} unconnected interfaces")
        try:
            cable = nb.dcim.cables.create(
                a_terminations=[{"object_type": "dcim.interface", "object_id": interfaces[0].id}],
                b_terminations=[{"object_type": "dcim.interface", "object_id": interfaces[1].id}],
                tags=[tag.id]
            )
            print(f"Created cable: {cable} with tags: {cable.tags}")

            # Now test the issue - THIS IS THE ACTUAL BUG FROM ISSUE #502
            print("\n" + "="*60)
            print("TESTING ISSUE #502: Setting tags to list of integers")
            print("="*60)
            print(f"Tags type: {type(cable.tags)}")
            if cable.tags:
                print(f"First tag type: {type(cable.tags[0])}")
                print(f"First tag: {cable.tags[0]}")

            # This is what the user reported in issue #502
            print(f"\nSetting cable.tags = [{tag.id}]")
            cable.tags = [tag.id]
            print(f"cable.tags is now: {cable.tags}")

            print("\nCalling cable.save()...")
            result = cable.save()
            print(f"Save result: {result}")
            print("SUCCESS! Issue #502 appears to be fixed!")

            # Clean up
            cable.delete()
            print("\nCleaned up test cable")

        except AttributeError as e:
            print(f"\n*** ISSUE #502 REPRODUCED! ***")
            print(f"AttributeError: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"ERROR creating/testing cable: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Not enough unconnected interfaces found. Trying to use an existing cable...")
        if cables:
            cable = cables[0]
            print(f"\nUsing existing cable: {cable} (ID: {cable.id})")

            # Test the issue
            print("\n" + "="*60)
            print("TESTING ISSUE #502: Setting tags to list of integers")
            print("="*60)
            original_tags = cable.tags
            print(f"Original tags: {original_tags}")

            print(f"\nSetting cable.tags = [{tag.id}]")
            cable.tags = [tag.id]
            print(f"cable.tags is now: {cable.tags}")

            try:
                print("\nCalling cable.save()...")
                result = cable.save()
                print(f"Save result: {result}")
                print("SUCCESS! Issue #502 appears to be fixed!")
            except AttributeError as e:
                print(f"\n*** ISSUE #502 REPRODUCED! ***")
                print(f"AttributeError: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Restore original tags
                cable.tags = original_tags
                try:
                    cable.save()
                    print("\nRestored original tags")
                except:
                    pass
        else:
            print("No cables available for testing.")
    """
