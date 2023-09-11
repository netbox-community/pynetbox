from importlib.metadata import version

from pynetbox.core.query import RequestError, AllocationError, ContentError
from pynetbox.core.api import Api as api

__version__ = version(__name__)
