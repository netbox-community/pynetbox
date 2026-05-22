"""
Shipped pynetbox extensions for popular NetBox plugins.

Each module here exposes an `Extension` subclass that can be passed to
`pynetbox.api(extensions=[...])`. See `pynetbox.core.extension` for the
extension contract and `docs/extensions.md` for a user-facing guide.
"""

from pynetbox.extensions.branching import BranchingExtension
from pynetbox.extensions.custom_objects import CustomObjectsExtension

__all__ = ("BranchingExtension", "CustomObjectsExtension")
