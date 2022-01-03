from pkg_resources import get_distribution, DistributionNotFound

from pynetbox.core.query import RequestError, AllocationError, ContentError
from pynetbox.core.api import Api as api
from pynetbox.core.app import register_models

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass
