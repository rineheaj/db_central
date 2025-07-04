"""
DatabaseManager - Main class for DB Central library providing simplified database operations.
"""

import logging
from typing import List, Optional, Dict, Any, Union
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine

from .models import Author, Book
from .exceptions import (
    DBCentralError, 
    ConnectionError, 
    QueryError, 
    ValidationError, 
    NotFoundError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Main database manager class that provides a simplified API for database operations.
    
    This class abstracts SQL complexities and provides intuitive methods for
    Create, Read, Update, and Delete (CRUD) operations.
    """
    
    def __init__(self, database_url: str = "sqlite:///db_central.db", echo: bool = False):
        """
        Initialize the database manager.
        
        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements for debugging
            
        Raises:
            ConnectionError: If database connection fails
        """
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[Engine] = None
        self._connect()
        
    def _connect(self):
        """Establish database connection and create tables."""
        try:
            self._engine = create_engine(self.database_url, echo=self.echo)
            SQLModel.metadata.create_all(self._engine)
            logger.info(f"Successfully connected to database: {self.database_url}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
            
    def _get_session(self) -> Session:
        """Get a database session."""
        if not self._engine:
            raise ConnectionError("Database not connected")
        return Session(self._engine)
    
    def _validate_string(self, value: Any, field_name: str, max_length: Optional[int] = None) -> str:
        """Validate string input."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
        return value.strip()
    
    # ==================== AUTHOR OPERATIONS ====================
    
    def create_author(self, name: str, email: str) -> Author:
        """
        Create a new author.
        
        Args:
            name: Author's full name
            email: Author's email address
            
        Returns:
            Author: The created author object
            
        Raises:
            ValidationError: If input validation fails
            QueryError: If database operation fails
            
        Example:
            >>> db = DatabaseManager()
            >>> author = db.create_author("Jane Doe", "jane@example.com")
            >>> print(f"Created author: {author.name}")
        """
        try:
            # Validate inputs
            name = self._validate_string(name, "name", 100)
            email = self._validate_string(email, "email", 100)
            
            # Basic email validation
            if "@" not in email:
                raise ValidationError("Email must contain @ symbol")
            
            with self._get_session() as session:
                # Check if author with this email already exists
                existing = session.exec(select(Author).where(Author.email == email)).first()
                if existing:
                    raise ValidationError(f"Author with email {email} already exists")
                
                author = Author(name=name, email=email)
                session.add(author)
                session.commit()
                session.refresh(author)
                logger.info(f"Created author: {author.name} (ID: {author.id})")
                return author
                
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to create author: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error creating author: {str(e)}")
    
    def get_author(self, author_id: int) -> Author:
        """
        Get an author by ID.
        
        Args:
            author_id: The author's ID
            
        Returns:
            Author: The author object
            
        Raises:
            ValidationError: If author_id is invalid
            NotFoundError: If author is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(author_id, int) or author_id <= 0:
                raise ValidationError("Author ID must be a positive integer")
                
            with self._get_session() as session:
                author = session.get(Author, author_id)
                if not author:
                    raise NotFoundError(f"Author with ID {author_id} not found")
                return author
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get author: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting author: {str(e)}")
    
    def get_all_authors(self) -> List[Author]:
        """
        Get all authors.
        
        Returns:
            List[Author]: List of all authors
            
        Raises:
            QueryError: If database operation fails
        """
        try:
            with self._get_session() as session:
                authors = session.exec(select(Author)).all()
                return list(authors)
                
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get authors: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting authors: {str(e)}")
    
    def update_author(self, author_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Author:
        """
        Update an author's information.
        
        Args:
            author_id: The author's ID
            name: New name (optional)
            email: New email (optional)
            
        Returns:
            Author: The updated author object
            
        Raises:
            ValidationError: If input validation fails
            NotFoundError: If author is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(author_id, int) or author_id <= 0:
                raise ValidationError("Author ID must be a positive integer")
                
            with self._get_session() as session:
                author = session.get(Author, author_id)
                if not author:
                    raise NotFoundError(f"Author with ID {author_id} not found")
                
                if name is not None:
                    author.name = self._validate_string(name, "name", 100)
                    
                if email is not None:
                    email = self._validate_string(email, "email", 100)
                    if "@" not in email:
                        raise ValidationError("Email must contain @ symbol")
                    
                    # Check if another author has this email
                    existing = session.exec(
                        select(Author).where(Author.email == email, Author.id != author_id)
                    ).first()
                    if existing:
                        raise ValidationError(f"Another author with email {email} already exists")
                    
                    author.email = email
                
                session.commit()
                session.refresh(author)
                logger.info(f"Updated author: {author.name} (ID: {author.id})")
                return author
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to update author: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error updating author: {str(e)}")
    
    def delete_author(self, author_id: int) -> bool:
        """
        Delete an author and all their books.
        
        Args:
            author_id: The author's ID
            
        Returns:
            bool: True if author was deleted
            
        Raises:
            ValidationError: If author_id is invalid
            NotFoundError: If author is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(author_id, int) or author_id <= 0:
                raise ValidationError("Author ID must be a positive integer")
                
            with self._get_session() as session:
                author = session.get(Author, author_id)
                if not author:
                    raise NotFoundError(f"Author with ID {author_id} not found")
                
                # Delete all books by this author first
                books = session.exec(select(Book).where(Book.author_id == author_id)).all()
                for book in books:
                    session.delete(book)
                
                session.delete(author)
                session.commit()
                logger.info(f"Deleted author: {author.name} (ID: {author_id}) and {len(books)} books")
                return True
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to delete author: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error deleting author: {str(e)}")
    
    # ==================== BOOK OPERATIONS ====================
    
    def create_book(self, title: str, content: str, author_id: int) -> Book:
        """
        Create a new book.
        
        Args:
            title: Book title
            content: Book content or description
            author_id: ID of the author
            
        Returns:
            Book: The created book object
            
        Raises:
            ValidationError: If input validation fails
            NotFoundError: If author is not found
            QueryError: If database operation fails
        """
        try:
            # Validate inputs
            title = self._validate_string(title, "title", 200)
            content = self._validate_string(content, "content")
            
            if not isinstance(author_id, int) or author_id <= 0:
                raise ValidationError("Author ID must be a positive integer")
            
            with self._get_session() as session:
                # Check if author exists
                author = session.get(Author, author_id)
                if not author:
                    raise NotFoundError(f"Author with ID {author_id} not found")
                
                book = Book(title=title, content=content, author_id=author_id)
                session.add(book)
                session.commit()
                session.refresh(book)
                logger.info(f"Created book: {book.title} (ID: {book.id})")
                return book
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to create book: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error creating book: {str(e)}")
    
    def get_book(self, book_id: int) -> Book:
        """
        Get a book by ID.
        
        Args:
            book_id: The book's ID
            
        Returns:
            Book: The book object
            
        Raises:
            ValidationError: If book_id is invalid
            NotFoundError: If book is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(book_id, int) or book_id <= 0:
                raise ValidationError("Book ID must be a positive integer")
                
            with self._get_session() as session:
                book = session.get(Book, book_id)
                if not book:
                    raise NotFoundError(f"Book with ID {book_id} not found")
                return book
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get book: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting book: {str(e)}")
    
    def get_all_books(self) -> List[Book]:
        """
        Get all books.
        
        Returns:
            List[Book]: List of all books
            
        Raises:
            QueryError: If database operation fails
        """
        try:
            with self._get_session() as session:
                books = session.exec(select(Book)).all()
                return list(books)
                
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get books: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting books: {str(e)}")
    
    def get_books_by_author(self, author_id: int) -> List[Book]:
        """
        Get all books by a specific author.
        
        Args:
            author_id: The author's ID
            
        Returns:
            List[Book]: List of books by the author
            
        Raises:
            ValidationError: If author_id is invalid
            NotFoundError: If author is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(author_id, int) or author_id <= 0:
                raise ValidationError("Author ID must be a positive integer")
                
            with self._get_session() as session:
                # Check if author exists
                author = session.get(Author, author_id)
                if not author:
                    raise NotFoundError(f"Author with ID {author_id} not found")
                
                books = session.exec(select(Book).where(Book.author_id == author_id)).all()
                return list(books)
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get books by author: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting books by author: {str(e)}")
    
    def update_book(self, book_id: int, title: Optional[str] = None, 
                   content: Optional[str] = None, author_id: Optional[int] = None) -> Book:
        """
        Update a book's information.
        
        Args:
            book_id: The book's ID
            title: New title (optional)
            content: New content (optional) 
            author_id: New author ID (optional)
            
        Returns:
            Book: The updated book object
            
        Raises:
            ValidationError: If input validation fails
            NotFoundError: If book or author is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(book_id, int) or book_id <= 0:
                raise ValidationError("Book ID must be a positive integer")
                
            with self._get_session() as session:
                book = session.get(Book, book_id)
                if not book:
                    raise NotFoundError(f"Book with ID {book_id} not found")
                
                if title is not None:
                    book.title = self._validate_string(title, "title", 200)
                    
                if content is not None:
                    book.content = self._validate_string(content, "content")
                    
                if author_id is not None:
                    if not isinstance(author_id, int) or author_id <= 0:
                        raise ValidationError("Author ID must be a positive integer")
                    
                    # Check if new author exists
                    author = session.get(Author, author_id)
                    if not author:
                        raise NotFoundError(f"Author with ID {author_id} not found")
                    
                    book.author_id = author_id
                
                session.commit()
                session.refresh(book)
                logger.info(f"Updated book: {book.title} (ID: {book.id})")
                return book
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to update book: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error updating book: {str(e)}")
    
    def delete_book(self, book_id: int) -> bool:
        """
        Delete a book.
        
        Args:
            book_id: The book's ID
            
        Returns:
            bool: True if book was deleted
            
        Raises:
            ValidationError: If book_id is invalid
            NotFoundError: If book is not found
            QueryError: If database operation fails
        """
        try:
            if not isinstance(book_id, int) or book_id <= 0:
                raise ValidationError("Book ID must be a positive integer")
                
            with self._get_session() as session:
                book = session.get(Book, book_id)
                if not book:
                    raise NotFoundError(f"Book with ID {book_id} not found")
                
                session.delete(book)
                session.commit()
                logger.info(f"Deleted book: {book.title} (ID: {book_id})")
                return True
                
        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to delete book: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error deleting book: {str(e)}")
    
    # ==================== UTILITY METHODS ====================
    
    def search_books(self, query: str) -> List[Book]:
        """
        Search for books by title or content.
        
        Args:
            query: Search query string
            
        Returns:
            List[Book]: List of matching books
            
        Raises:
            ValidationError: If query is invalid
            QueryError: If database operation fails
        """
        try:
            query = self._validate_string(query, "search query")
            query_pattern = f"%{query}%"
            
            with self._get_session() as session:
                books = session.exec(
                    select(Book).where(
                        (Book.title.contains(query)) | (Book.content.contains(query))
                    )
                ).all()
                return list(books)
                
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to search books: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error searching books: {str(e)}")
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get basic database statistics.
        
        Returns:
            Dict[str, int]: Dictionary with author and book counts
            
        Raises:
            QueryError: If database operation fails
        """
        try:
            with self._get_session() as session:
                author_count = len(session.exec(select(Author)).all())
                book_count = len(session.exec(select(Book)).all())
                
                return {
                    "authors": author_count,
                    "books": book_count
                }
                
        except SQLAlchemyError as e:
            raise QueryError(f"Failed to get database stats: {str(e)}")
        except Exception as e:
            raise DBCentralError(f"Unexpected error getting database stats: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()