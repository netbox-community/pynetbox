import pynetbox
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

POWER_PORT_ID = 82
POWER_OUTLET_ID = 153

nb = pynetbox.api(
    "http://127.0.0.1:8000/",
    token="1ea49c43cfd32ef777c7f7c9ae56477f14f7ab55",
    threading=True,
)


def print_object_details(objects, object_type="Object"):
    """Print details for a list of NetBox objects.

    Args:
        objects: List of NetBox objects to print details for
        object_type (str): Type of object being printed (for logging purposes)
    """
    count = 0
    for obj in objects:
        print("----------------------------------")
        print(f"{object_type}: {obj}")
        print(f"Trace: {obj.trace()}")
        print("----------------------------------")
        count += 1
        if count > 3:
            return


def print_all_object_types():
    """Print details for all supported NetBox object types."""
    object_types = {
        "Interfaces": nb.dcim.interfaces,
        "Power Feeds": nb.dcim.power_feeds,
        "Power Outlets": nb.dcim.power_outlets,
        "Power Ports": nb.dcim.power_ports,
        "Console Ports": nb.dcim.console_ports,
        "Console Server Ports": nb.dcim.console_server_ports,
        "Front Ports": nb.dcim.front_ports,
        "Rear Ports": nb.dcim.rear_ports,
    }

    for object_type, endpoint in object_types.items():
        print(f"\n{object_type}")
        try:
            objects = endpoint.all()
            print_object_details(objects, object_type)
        except Exception as e:
            print(f"Error fetching {object_type}: {str(e)}")


def is_branch_ready(branch):
    """Check if branch status is READY."""
    return branch.status == "ready"


@retry(
    stop=stop_after_attempt(30),  # Try for up to 30 attempts
    wait=wait_exponential(
        multiplier=1, min=4, max=60
    ),  # Wait between 4-60 seconds, increasing exponentially
    retry=retry_if_result(
        lambda x: not is_branch_ready(x)
    ),  # Retry if branch is not ready
)
def wait_for_branch_ready(branch):
    """Wait for branch to be ready, with exponential backoff."""
    print(f"Checking branch status: {branch.status}")
    return branch


# Run the function to print all object types
# print_all_object_types()

print("----------------------------------")
sites = nb.dcim.sites.all()
print(f"Sites: {len(sites)}")
for site in sites:
    print(site)
print("----------------------------------")
branches = nb.plugins.branching.branches.all()
print(f"Branches: {len(branches)}")

branch = nb.plugins.branching.branches.create(name="testbranch")
print(branch)
print(f"branch status: {branch.status}")

# Wait for branch to be ready
branch = wait_for_branch_ready(branch)
print(f"Branch is now ready! Status: {branch.status}")

with nb.activate_branch(branch):
    print("----------------------------------")
    sites = nb.dcim.sites.all()
    print(f"Sites: {len(sites)}")
    for site in sites:
        print(site)
    print("----------------------------------")
