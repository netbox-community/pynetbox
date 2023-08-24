from importlib.metadata import metadata

from pynetbox.core.query import RequestError, AllocationError, ContentError
from pynetbox.core.api import Api as api

__version__ = metadata(__name__).get('Version')
