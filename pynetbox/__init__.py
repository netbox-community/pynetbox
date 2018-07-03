from pkg_resources import get_distribution, DistributionNotFound

from pynetbox.api import Api as api
from pynetbox.lib import RequestError

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass
