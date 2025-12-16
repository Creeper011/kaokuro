from src.domain.enum.error_types import ErrorTypes

class Error():
    """Represents an exception with an error type"""
    error_type: ErrorTypes
    exception: Exception