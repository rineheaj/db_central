"""Tests for the DatabaseManager high-level API."""

import pytest
from sqlmodel import SQLModel
from db_central import (
    DatabaseManager, 
    Author, 
    Book,
    DatabaseError,
    ConnectionError,
    ValidationError
)


@pytest.fixture
def db_manager():
    """Create a test DatabaseManager with in-memory SQLite."""
    manager = DatabaseManager("sqlite:///:memory:", echo=False)
    manager.initialize_tables()
    return manager


@pytest.fixture
def sample_author():
    """Create a sample author for testing."""
    return Author(name="Test Author", email="test@example.com")


@pytest.fixture
def sample_book(sample_author):
    """Create a sample book for testing."""
    return Book(title="Test Book", content="Test content", author_id=1)


class TestDatabaseManager:
    """Test cases for DatabaseManager."""
    
    def test_initialization(self):
        """Test DatabaseManager initialization."""
        manager = DatabaseManager("sqlite:///:memory:")
        assert manager.database_url == "sqlite:///:memory:"
        assert manager._engine is not None
    
    def test_initialization_with_invalid_url(self):
        """Test initialization with invalid database URL."""
        with pytest.raises(ConnectionError):
            DatabaseManager("invalid://url")
    
    def test_initialize_tables(self, db_manager):
        """Test table initialization."""
        # Should not raise any exception
        db_manager.initialize_tables()
    
    def test_create_author(self, db_manager, sample_author):
        """Test creating an author."""
        created_author = db_manager.create(sample_author)
        
        assert created_author.id is not None
        assert created_author.name == "Test Author"
        assert created_author.email == "test@example.com"
    
    def test_create_with_invalid_object(self, db_manager):
        """Test creating with invalid object type."""
        with pytest.raises(ValidationError):
            db_manager.create("not a model")
    
    def test_get_by_id(self, db_manager, sample_author):
        """Test retrieving a record by ID."""
        created_author = db_manager.create(sample_author)
        retrieved_author = db_manager.get_by_id(Author, created_author.id)
        
        assert retrieved_author is not None
        assert retrieved_author.id == created_author.id
        assert retrieved_author.name == created_author.name
    
    def test_get_by_id_not_found(self, db_manager):
        """Test retrieving a non-existent record."""
        result = db_manager.get_by_id(Author, 999)
        assert result is None
    
    def test_get_by_id_invalid_params(self, db_manager):
        """Test get_by_id with invalid parameters."""
        with pytest.raises(ValidationError):
            db_manager.get_by_id("not a model", 1)
        
        with pytest.raises(ValidationError):
            db_manager.get_by_id(Author, -1)
        
        with pytest.raises(ValidationError):
            db_manager.get_by_id(Author, "not an int")
    
    def test_get_all(self, db_manager, sample_author):
        """Test retrieving all records."""
        # Create multiple authors
        author1 = db_manager.create(sample_author)
        author2 = db_manager.create(Author(name="Author 2", email="author2@example.com"))
        
        all_authors = db_manager.get_all(Author)
        assert len(all_authors) == 2
        
        author_ids = [author.id for author in all_authors]
        assert author1.id in author_ids
        assert author2.id in author_ids
    
    def test_get_all_with_limit(self, db_manager, sample_author):
        """Test retrieving records with limit."""
        # Create multiple authors
        db_manager.create(sample_author)
        db_manager.create(Author(name="Author 2", email="author2@example.com"))
        db_manager.create(Author(name="Author 3", email="author3@example.com"))
        
        limited_authors = db_manager.get_all(Author, limit=2)
        assert len(limited_authors) == 2
    
    def test_get_all_invalid_model(self, db_manager):
        """Test get_all with invalid model class."""
        with pytest.raises(ValidationError):
            db_manager.get_all("not a model")
    
    def test_update(self, db_manager, sample_author):
        """Test updating a record."""
        created_author = db_manager.create(sample_author)
        
        # Update the author
        created_author.name = "Updated Author"
        updated_author = db_manager.update(created_author)
        
        assert updated_author.name == "Updated Author"
        assert updated_author.id == created_author.id
    
    def test_update_invalid_object(self, db_manager):
        """Test updating with invalid object."""
        with pytest.raises(ValidationError):
            db_manager.update("not a model")
        
        # Test object without ID
        author_without_id = Author(name="No ID", email="noid@example.com")
        with pytest.raises(ValidationError):
            db_manager.update(author_without_id)
    
    def test_delete(self, db_manager, sample_author):
        """Test deleting a record."""
        created_author = db_manager.create(sample_author)
        
        # Delete the author
        result = db_manager.delete(Author, created_author.id)
        assert result is True
        
        # Verify it's deleted
        retrieved_author = db_manager.get_by_id(Author, created_author.id)
        assert retrieved_author is None
    
    def test_delete_not_found(self, db_manager):
        """Test deleting a non-existent record."""
        result = db_manager.delete(Author, 999)
        assert result is False
    
    def test_delete_invalid_params(self, db_manager):
        """Test delete with invalid parameters."""
        with pytest.raises(ValidationError):
            db_manager.delete("not a model", 1)
        
        with pytest.raises(ValidationError):
            db_manager.delete(Author, -1)
    
    def test_find_by(self, db_manager, sample_author):
        """Test finding records by field values."""
        created_author = db_manager.create(sample_author)
        
        # Find by name
        found_authors = db_manager.find_by(Author, name="Test Author")
        assert len(found_authors) == 1
        assert found_authors[0].id == created_author.id
        
        # Find by email
        found_authors = db_manager.find_by(Author, email="test@example.com")
        assert len(found_authors) == 1
        assert found_authors[0].id == created_author.id
        
        # Find by non-existent value
        found_authors = db_manager.find_by(Author, name="Non-existent")
        assert len(found_authors) == 0
    
    def test_find_by_invalid_field(self, db_manager):
        """Test find_by with invalid field name."""
        with pytest.raises(ValidationError):
            db_manager.find_by(Author, non_existent_field="value")
    
    def test_find_by_invalid_model(self, db_manager):
        """Test find_by with invalid model class."""
        with pytest.raises(ValidationError):
            db_manager.find_by("not a model", name="test")
    
    def test_book_with_author_relationship(self, db_manager, sample_author):
        """Test creating books with author relationships."""
        # Create author first
        created_author = db_manager.create(sample_author)
        
        # Create book with author relationship
        book = Book(title="Test Book", content="Test content", author_id=created_author.id)
        created_book = db_manager.create(book)
        
        assert created_book.id is not None
        assert created_book.author_id == created_author.id
        
        # Retrieve book and verify relationship
        retrieved_book = db_manager.get_by_id(Book, created_book.id)
        assert retrieved_book.author_id == created_author.id
    
    def test_session_context_manager(self, db_manager):
        """Test the session context manager."""
        with db_manager.session() as session:
            author = Author(name="Context Author", email="context@example.com")
            session.add(author)
            # Should auto-commit when exiting context
        
        # Verify the author was saved
        found_authors = db_manager.find_by(Author, name="Context Author")
        assert len(found_authors) == 1


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_database_manager(self):
        """Test the convenience function for creating DatabaseManager."""
        from db_central import create_database_manager
        
        manager = create_database_manager("sqlite:///:memory:", echo=True)
        assert isinstance(manager, DatabaseManager)
        assert manager.database_url == "sqlite:///:memory:"
        assert manager.echo is True


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_database_not_connected_session(self):
        """Test session creation when database not connected."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager._engine = None  # Simulate disconnection
        
        with pytest.raises(DatabaseError):
            with manager.session():
                pass


if __name__ == "__main__":
    pytest.main([__file__])