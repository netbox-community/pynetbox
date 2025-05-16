Branching Plugin
================

The NetBox branching plugin allows you to create and work with branches in NetBox, similar to version control systems. This enables you to make changes in isolation and merge them back to the main branch when ready.

Activating Branches
-----------------

The `activate_branch` context manager allows you to perform operations within a specific branch's schema. All operations performed within the context manager will use that branch's schema.

.. code-block:: python

    import pynetbox
    
    # Initialize the API
    nb = pynetbox.api(
        "http://localhost:8000",
        token="your-token-here"
    )
    
    # Get a new branch
    branch = nb.plugins.branching.branches.get(id=1)
    
    # Activate the branch for operations
    with nb.activate_branch(branch):
        # All operations within this block will use the branch's schema
        sites = nb.dcim.sites.all()
        # Make changes to objects...
        # These changes will only exist in this branch

Waiting for Branch Status
-----------------------

When working with branches, you often need to wait for certain status changes, such as when a branch becomes ready after creation or when a merge operation completes. The `tenacity`_ library provides a robust way to handle these waiting scenarios.

First, install tenacity:

.. code-block:: bash

    pip install tenacity

Here's how to use tenacity to wait for branch status changes:

.. code-block:: python

    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result
    
    def is_branch_status(branch, target_status):
        return str(branch.status) == target_status
    
    @retry(
        stop=stop_after_attempt(30),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_result(lambda x: not is_branch_status(x, target_status))
    )
    def wait_for_branch_status(branch, target_status):
        """Wait for branch to reach a specific status, with exponential backoff."""
        branch = nb.plugins.branching.branches.get(branch.id)
        return branch
    
    # Wait for a newly created branch to be ready
    branch = nb.plugins.branching.branches.create(name="testbranch")
    branch = wait_for_branch_status(branch, "Ready")
    
    # Or wait for a merge operation to complete
    merge_result = nb.plugins.branching.branches.merge(branch)
    branch = wait_for_branch_status(merge_result, "Merged")

The retry configuration:
- Tries up to 30 times
- Uses exponential backoff starting at 4 seconds, up to 60 seconds
- Checks the branch status by fetching the latest branch data
- Continues retrying until the branch reaches the target status

.. _tenacity: https://github.com/jd/tenacity

