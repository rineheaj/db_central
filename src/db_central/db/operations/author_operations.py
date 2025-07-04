"""
Author operations: High-level functions for Author model CRUD operations.
"""

from typing import List, Optional
from db_central.database_manager import DatabaseManager
from db_central.db.models.author_and_book import Author


def create_author(db_manager: DatabaseManager, name: str, email: str) -> Author:
    """
    Create a new author.
    
    Args:
        db_manager: DatabaseManager instance
        name: Author's name
        email: Author's email
        
    Returns:
        Created Author instance
    """
    author = Author(name=name, email=email)
    return db_manager.create(author)


def get_author(db_manager: DatabaseManager, author_id: int) -> Optional[Author]:
    """
    Get an author by ID.
    
    Args:
        db_manager: DatabaseManager instance
        author_id: Author's ID
        
    Returns:
        Author instance if found, None otherwise
    """
    return db_manager.read(Author, author_id)


def get_all_authors(db_manager: DatabaseManager, limit: Optional[int] = None) -> List[Author]:
    """
    Get all authors.
    
    Args:
        db_manager: DatabaseManager instance
        limit: Maximum number of authors to return
        
    Returns:
        List of Author instances
    """
    return db_manager.read_all(Author, limit)


def update_author(db_manager: DatabaseManager, author: Author) -> Author:
    """
    Update an existing author.
    
    Args:
        db_manager: DatabaseManager instance
        author: Author instance to update
        
    Returns:
        Updated Author instance
    """
    return db_manager.update(author)


def delete_author(db_manager: DatabaseManager, author_id: int) -> bool:
    """
    Delete an author by ID.
    
    Args:
        db_manager: DatabaseManager instance
        author_id: Author's ID
        
    Returns:
        True if author was deleted, False if not found
    """
    return db_manager.delete(Author, author_id)


def find_authors_by_name(db_manager: DatabaseManager, name: str) -> List[Author]:
    """
    Find authors by name.
    
    Args:
        db_manager: DatabaseManager instance
        name: Author's name to search for
        
    Returns:
        List of matching Author instances
    """
    return db_manager.query(Author, {"name": name})


def find_authors_by_email(db_manager: DatabaseManager, email: str) -> List[Author]:
    """
    Find authors by email.
    
    Args:
        db_manager: DatabaseManager instance
        email: Author's email to search for
        
    Returns:
        List of matching Author instances
    """
    return db_manager.query(Author, {"email": email})