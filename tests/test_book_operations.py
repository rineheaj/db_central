"""
Tests for DatabaseManager book operations.
"""

import pytest
from db_central.exceptions import ValidationError, NotFoundError, QueryError


class TestBookOperations:
    """Test suite for book CRUD operations."""
    
    def test_create_book_success(self, memory_db, sample_author):
        """Test successful book creation."""
        book = memory_db.create_book("Test Book", "Test content", sample_author.id)
        
        assert book.id is not None
        assert book.title == "Test Book"
        assert book.content == "Test content"
        assert book.author_id == sample_author.id
    
    def test_create_book_validation_errors(self, memory_db, sample_author):
        """Test book creation validation errors."""
        # Empty title
        with pytest.raises(ValidationError, match="title cannot be empty"):
            memory_db.create_book("", "Content", sample_author.id)
        
        # Empty content
        with pytest.raises(ValidationError, match="content cannot be empty"):
            memory_db.create_book("Title", "", sample_author.id)
        
        # Title too long
        with pytest.raises(ValidationError, match="title cannot exceed 200 characters"):
            memory_db.create_book("A" * 201, "Content", sample_author.id)
        
        # Invalid author ID
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.create_book("Title", "Content", -1)
    
    def test_create_book_author_not_found(self, memory_db):
        """Test creating book with non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.create_book("Title", "Content", 99999)
    
    def test_get_book_success(self, memory_db, sample_book):
        """Test successful book retrieval."""
        retrieved = memory_db.get_book(sample_book.id)
        
        assert retrieved.id == sample_book.id
        assert retrieved.title == sample_book.title
        assert retrieved.content == sample_book.content
        assert retrieved.author_id == sample_book.author_id
    
    def test_get_book_not_found(self, memory_db):
        """Test getting non-existent book."""
        with pytest.raises(NotFoundError, match="Book with ID 99999 not found"):
            memory_db.get_book(99999)
    
    def test_get_book_invalid_id(self, memory_db):
        """Test getting book with invalid ID."""
        with pytest.raises(ValidationError, match="Book ID must be a positive integer"):
            memory_db.get_book(-1)
        
        with pytest.raises(ValidationError, match="Book ID must be a positive integer"):
            memory_db.get_book(0)
    
    def test_get_all_books(self, memory_db, sample_author):
        """Test getting all books."""
        # Initially empty
        books = memory_db.get_all_books()
        assert len(books) == 0
        
        # Add some books
        book1 = memory_db.create_book("Book 1", "Content 1", sample_author.id)
        book2 = memory_db.create_book("Book 2", "Content 2", sample_author.id)
        
        books = memory_db.get_all_books()
        assert len(books) == 2
        
        book_ids = [b.id for b in books]
        assert book1.id in book_ids
        assert book2.id in book_ids
    
    def test_get_books_by_author(self, memory_db):
        """Test getting books by specific author."""
        # Create two authors
        author1 = memory_db.create_author("Author 1", "author1@example.com")
        author2 = memory_db.create_author("Author 2", "author2@example.com")
        
        # Create books for each author
        book1 = memory_db.create_book("Book 1", "Content 1", author1.id)
        book2 = memory_db.create_book("Book 2", "Content 2", author1.id)
        book3 = memory_db.create_book("Book 3", "Content 3", author2.id)
        
        # Test getting books by author1
        author1_books = memory_db.get_books_by_author(author1.id)
        assert len(author1_books) == 2
        book_ids = [b.id for b in author1_books]
        assert book1.id in book_ids
        assert book2.id in book_ids
        assert book3.id not in book_ids
        
        # Test getting books by author2
        author2_books = memory_db.get_books_by_author(author2.id)
        assert len(author2_books) == 1
        assert author2_books[0].id == book3.id
    
    def test_get_books_by_author_not_found(self, memory_db):
        """Test getting books by non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.get_books_by_author(99999)
    
    def test_get_books_by_author_invalid_id(self, memory_db):
        """Test getting books by author with invalid ID."""
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.get_books_by_author(-1)
    
    def test_update_book_success(self, memory_db, sample_book, sample_author):
        """Test successful book update."""
        # Update title only
        updated = memory_db.update_book(sample_book.id, title="Updated Title")
        assert updated.title == "Updated Title"
        assert updated.content == sample_book.content
        assert updated.author_id == sample_book.author_id
        
        # Update content only
        updated = memory_db.update_book(sample_book.id, content="Updated content")
        assert updated.content == "Updated content"
        assert updated.title == "Updated Title"  # Previous update should persist
        
        # Create another author and update author_id
        author2 = memory_db.create_author("Author 2", "author2@example.com")
        updated = memory_db.update_book(sample_book.id, author_id=author2.id)
        assert updated.author_id == author2.id
        
        # Update all fields
        updated = memory_db.update_book(sample_book.id, 
                                      title="Final Title", 
                                      content="Final content",
                                      author_id=sample_author.id)
        assert updated.title == "Final Title"
        assert updated.content == "Final content"
        assert updated.author_id == sample_author.id
    
    def test_update_book_not_found(self, memory_db):
        """Test updating non-existent book."""
        with pytest.raises(NotFoundError, match="Book with ID 99999 not found"):
            memory_db.update_book(99999, title="New Title")
    
    def test_update_book_author_not_found(self, memory_db, sample_book):
        """Test updating book with non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.update_book(sample_book.id, author_id=99999)
    
    def test_update_book_validation_errors(self, memory_db, sample_book):
        """Test book update validation errors."""
        # Invalid title
        with pytest.raises(ValidationError, match="title cannot be empty"):
            memory_db.update_book(sample_book.id, title="")
        
        # Invalid content
        with pytest.raises(ValidationError, match="content cannot be empty"):
            memory_db.update_book(sample_book.id, content="")
        
        # Invalid author ID
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.update_book(sample_book.id, author_id=-1)
    
    def test_delete_book_success(self, memory_db, sample_book):
        """Test successful book deletion."""
        result = memory_db.delete_book(sample_book.id)
        assert result is True
        
        # Verify book is deleted
        with pytest.raises(NotFoundError):
            memory_db.get_book(sample_book.id)
    
    def test_delete_book_not_found(self, memory_db):
        """Test deleting non-existent book."""
        with pytest.raises(NotFoundError, match="Book with ID 99999 not found"):
            memory_db.delete_book(99999)
    
    def test_delete_book_invalid_id(self, memory_db):
        """Test deleting book with invalid ID."""
        with pytest.raises(ValidationError, match="Book ID must be a positive integer"):
            memory_db.delete_book(-1)
    
    def test_search_books(self, memory_db, sample_author):
        """Test book search functionality."""
        # Create test books
        book1 = memory_db.create_book("Python Programming", "Learn Python basics", sample_author.id)
        book2 = memory_db.create_book("Java Development", "Advanced Python techniques", sample_author.id)
        book3 = memory_db.create_book("Web Design", "HTML and CSS fundamentals", sample_author.id)
        
        # Search by title
        results = memory_db.search_books("Python")
        assert len(results) == 2  # Both book1 and book2 contain "Python"
        
        # Search by content
        results = memory_db.search_books("HTML")
        assert len(results) == 1
        assert results[0].id == book3.id
        
        # Search with no results
        results = memory_db.search_books("NoMatch")
        assert len(results) == 0
        
        # Case-insensitive search
        results = memory_db.search_books("python")
        assert len(results) == 2
    
    def test_search_books_validation_error(self, memory_db):
        """Test search books with invalid query."""
        with pytest.raises(ValidationError, match="search query cannot be empty"):
            memory_db.search_books("")