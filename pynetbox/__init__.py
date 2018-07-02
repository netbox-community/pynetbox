from setuptools_scm import get_version
from pynetbox.api import Api as api
from pynetbox.lib import RequestError


__version__ = get_version(root='..', relative_to=__file__)
