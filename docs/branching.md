# Branching Plugin

The NetBox branching plugin allows you to create and work with branches in NetBox, similar to version control systems. This enables you to make changes in isolation and merge them back to the main branch when ready.

## Activating Branches

The `activate_branch` context manager allows you to perform operations within a specific branch's schema. All operations performed within the context manager will use that branch's schema.

```python
import pynetbox

# Initialize the API
nb = pynetbox.api(
    "http://localhost:8000",
    token="your-token-here"
)

# Get an existing branch
branch = nb.plugins.branching.branches.get(id=1)

# Activate the branch for operations
with nb.activate_branch(branch):
    # All operations within this block will use the branch's schema
    sites = nb.dcim.sites.all()
    # Make changes to objects...
    # These changes will only exist in this branch
```

## Waiting for Branch Status

When working with branches, you often need to wait for certain status changes, such as when a branch becomes ready after creation or when a merge operation completes. The [tenacity](https://github.com/jd/tenacity) library provides a robust way to handle these waiting scenarios.

First, install tenacity:

```bash
pip install tenacity
```

Here's how to create a reusable function to wait for branch status changes:

```python
from tenacity import retry, retry_if_result, stop_after_attempt, wait_exponential
import pynetbox

@retry(
    stop=stop_after_attempt(30),  # Try for up to 30 attempts
    wait=wait_exponential(
        multiplier=1, min=4, max=60
    ),  # Wait between 4-60 seconds, increasing exponentially
    retry=retry_if_result(lambda x: not x),  # Retry if the status check returns False
)
def wait_for_branch_status(branch, target_status):
    """Wait for branch to reach a specific status, with exponential backoff."""
    branch = nb.plugins.branching.branches.get(branch.id)
    return str(branch.status) == target_status

# Example usage:
branch = nb.plugins.branching.branches.create(name="my-branch")

# Wait for branch to be ready
wait_for_branch_status(branch, "Ready")

# Get the latest branch status
branch = nb.plugins.branching.branches.get(branch.id)
print(f"Branch is now ready! Status: {branch.status}")
```

The function will:

1. Check the current status of the branch
2. If the status doesn't match the target status, it will retry with exponential backoff
3. Continue retrying until either:
    - The branch reaches the target status
    - The maximum number of attempts (30) is reached
    - The maximum wait time (60 seconds) is exceeded

The exponential backoff ensures that we don't overwhelm the server with requests while still checking frequently enough to catch status changes quickly. 