"""
DB Central: A Python library designed to simplify database interactions using SQLAlchemy/SQLModel.

This library provides a high-level API for database operations with error handling,
retry mechanisms, and intuitive CRUD operations.
"""

# Main API exports
from .database_manager import DatabaseManager, DatabaseError, ConnectionError, ValidationError

# Operation exports  
from .db.operations import author_operations, book_operations

# Legacy config for backwards compatibility
from .db.config.config_db import init_db, ENGINE, DB_URL

__version__ = "0.1.0"
__all__ = [
    "DatabaseManager", 
    "DatabaseError", 
    "ConnectionError", 
    "ValidationError",
    "author_operations",
    "book_operations",
    "init_db",
    "ENGINE",
    "DB_URL"
]


def main() -> None:
    print("Hello from db-central!")
