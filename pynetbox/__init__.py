from pynetbox.core.api import Api
from pynetbox.core.extension import Extension
from pynetbox.core.query import (
    AllocationError,
    ContentError,
    ParameterValidationError,
    RequestError,
)
from pynetbox.core.response import JsonField

__version__ = "7.8.0"

# Lowercase alias for backward compatibility
api = Api

__all__ = (
    "AllocationError",
    "Api",
    "ContentError",
    "Extension",
    "JsonField",
    "ParameterValidationError",
    "RequestError",
    "__version__",
    "api",
)
