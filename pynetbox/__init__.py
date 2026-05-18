from pynetbox.core.api import Api
from pynetbox.core.extension import Extension
from pynetbox.core.query import (
    AllocationError,
    ContentError,
    RequestError,
    ParameterValidationError,
)
from pynetbox.core.response import JsonField

__version__ = "7.7.0"

# Lowercase alias for backward compatibility
api = Api

__all__ = (
    "Api",
    "AllocationError",
    "ContentError",
    "Extension",
    "JsonField",
    "RequestError",
    "ParameterValidationError",
    "api",
    "__version__",
)
