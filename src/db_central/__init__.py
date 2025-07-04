"""
DB Central - A Python library for simplified database interactions using SQLAlchemy/SQLModel.

This library provides tools and utilities to streamline data management and accelerate 
application development with clean, intuitive APIs for database operations.
"""

# Import main classes for public API
from .database_manager import DatabaseManager, create_database_manager
from .exceptions import DatabaseError, ConnectionError, ValidationError

# Import models for convenience
from .db.models.author_and_book import Author, Book

__version__ = "0.1.0"
__all__ = [
    "DatabaseManager", 
    "create_database_manager",
    "DatabaseError", 
    "ConnectionError", 
    "ValidationError",
    "Author", 
    "Book"
]


def main() -> None:
    """Main entry point for the library."""
    print("Hello from db-central!")
