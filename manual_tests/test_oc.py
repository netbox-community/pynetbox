import pynetbox
import json

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="106cb162cafaf9d3de62eef949b53116289c06a9",
    threading=True,
)


# Test ObjectChanges from core app
print("Fetching object changes...")
object_changes = nb.core.object_changes.all()

count = 0
for oc in object_changes:
    if count >= 5:  # Limit to first 5 for readability
        break
    count += 1
    print(f"\n--- Object Change: {oc} ---")
    print(f"ID: {oc.id}")
    print(f"Request ID: {oc.request_id}")
    print(f"Action: {oc.action}")
    print(f"Changed Object Type: {oc.changed_object_type}")
    print(f"Changed Object ID: {oc.changed_object_id}")
    print(f"User: {oc.user}")
    print(f"Time: {oc.time}")

    # Display JSON fields
    if oc.prechange_data:
        print("\nPre-change Data:")
        print(json.dumps(oc.prechange_data, indent=2))

    if oc.postchange_data:
        print("\nPost-change Data:")
        print(json.dumps(oc.postchange_data, indent=2))

print(f"\n\nDisplayed first {count} object changes")
