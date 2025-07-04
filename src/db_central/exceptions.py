"""
Custom exceptions for DB Central library.
"""

class DBCentralError(Exception):
    """Base exception for all DB Central errors."""
    pass

class ConnectionError(DBCentralError):
    """Raised when database connection fails."""
    pass

class QueryError(DBCentralError):
    """Raised when SQL query execution fails."""
    pass

class ValidationError(DBCentralError):
    """Raised when input validation fails."""
    pass

class NotFoundError(DBCentralError):
    """Raised when requested record is not found."""
    pass