"""
Book operations: High-level functions for Book model CRUD operations.
"""

from typing import List, Optional
from db_central.database_manager import DatabaseManager
from db_central.db.models.author_and_book import Book


def create_book(db_manager: DatabaseManager, title: str, content: str, author_id: int) -> Book:
    """
    Create a new book.
    
    Args:
        db_manager: DatabaseManager instance
        title: Book's title
        content: Book's content
        author_id: ID of the book's author
        
    Returns:
        Created Book instance
    """
    book = Book(title=title, content=content, author_id=author_id)
    return db_manager.create(book)


def get_book(db_manager: DatabaseManager, book_id: int) -> Optional[Book]:
    """
    Get a book by ID.
    
    Args:
        db_manager: DatabaseManager instance
        book_id: Book's ID
        
    Returns:
        Book instance if found, None otherwise
    """
    return db_manager.read(Book, book_id)


def get_all_books(db_manager: DatabaseManager, limit: Optional[int] = None) -> List[Book]:
    """
    Get all books.
    
    Args:
        db_manager: DatabaseManager instance
        limit: Maximum number of books to return
        
    Returns:
        List of Book instances
    """
    return db_manager.read_all(Book, limit)


def update_book(db_manager: DatabaseManager, book: Book) -> Book:
    """
    Update an existing book.
    
    Args:
        db_manager: DatabaseManager instance
        book: Book instance to update
        
    Returns:
        Updated Book instance
    """
    return db_manager.update(book)


def delete_book(db_manager: DatabaseManager, book_id: int) -> bool:
    """
    Delete a book by ID.
    
    Args:
        db_manager: DatabaseManager instance
        book_id: Book's ID
        
    Returns:
        True if book was deleted, False if not found
    """
    return db_manager.delete(Book, book_id)


def find_books_by_title(db_manager: DatabaseManager, title: str) -> List[Book]:
    """
    Find books by title.
    
    Args:
        db_manager: DatabaseManager instance
        title: Book's title to search for
        
    Returns:
        List of matching Book instances
    """
    return db_manager.query(Book, {"title": title})


def find_books_by_author(db_manager: DatabaseManager, author_id: int) -> List[Book]:
    """
    Find books by author ID.
    
    Args:
        db_manager: DatabaseManager instance
        author_id: Author's ID to search for
        
    Returns:
        List of matching Book instances
    """
    return db_manager.query(Book, {"author_id": author_id})