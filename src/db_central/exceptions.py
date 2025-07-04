"""
Database exceptions for the db_central library.

This module contains custom exception classes used throughout the library
to provide meaningful error handling for database operations.
"""


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    pass


class ValidationError(DatabaseError):
    """Exception raised when data validation fails."""
    pass