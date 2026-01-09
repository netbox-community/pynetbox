from pynetbox.core.api import Api
from pynetbox.core.query import (
    AllocationError,
    ContentError,
    RequestError,
    ParameterValidationError,
)

__version__ = "7.6.0"

# Lowercase alias for backward compatibility
api = Api
