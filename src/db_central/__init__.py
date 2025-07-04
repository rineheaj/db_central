"""
DB Central - A Python SQL Wrapper Library

DB Central simplifies database interactions by providing an intuitive API
that abstracts SQL complexities for users unfamiliar with SQL models.
"""

from .database_manager import DatabaseManager
from .models import Author, Book
from .exceptions import (
    DBCentralError,
    ConnectionError,
    QueryError,
    ValidationError,
    NotFoundError
)

__version__ = "0.1.0"
__all__ = [
    "DatabaseManager",
    "Author", 
    "Book",
    "DBCentralError",
    "ConnectionError", 
    "QueryError",
    "ValidationError",
    "NotFoundError"
]

def create_database_manager(database_url: str = "sqlite:///db_central.db", echo: bool = False) -> DatabaseManager:
    """
    Factory function to create a DatabaseManager instance.
    
    Args:
        database_url: Database connection URL (defaults to SQLite)
        echo: Whether to echo SQL statements (useful for debugging)
        
    Returns:
        DatabaseManager: Configured database manager instance
        
    Example:
        >>> db = create_database_manager("sqlite:///my_app.db")
        >>> authors = db.get_all_authors()
    """
    return DatabaseManager(database_url=database_url, echo=echo)