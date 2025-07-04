"""
Tests for DatabaseManager utility functions and error handling.
"""

import pytest
import tempfile
import os
from db_central import create_database_manager
from db_central.exceptions import (
    DBCentralError,
    ConnectionError,
    ValidationError
)


class TestDatabaseManager:
    """Test suite for DatabaseManager initialization and utilities."""
    
    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization."""
        # Test with default parameters
        db = create_database_manager()
        assert db._engine is not None
        assert "sqlite" in db.database_url
        db.close()
        
        # Test with custom parameters
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        try:
            db = create_database_manager(f"sqlite:///{temp_path}", echo=True)
            assert db._engine is not None
            assert temp_path in db.database_url
            assert db.echo is True
            db.close()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_database_manager_invalid_url(self):
        """Test DatabaseManager with invalid database URL."""
        with pytest.raises(ConnectionError, match="Failed to connect to database"):
            create_database_manager("invalid://invalid_url")
    
    def test_context_manager(self):
        """Test DatabaseManager as context manager."""
        with create_database_manager("sqlite:///:memory:") as db:
            assert db._engine is not None
            
            # Perform some operations
            author = db.create_author("Test Author", "test@example.com")
            assert author.id is not None
        
        # Connection should be closed after context exit
        assert db._engine is None
    
    def test_get_database_stats(self, memory_db):
        """Test database statistics functionality."""
        # Initially empty
        stats = memory_db.get_database_stats()
        assert stats["authors"] == 0
        assert stats["books"] == 0
        
        # Add some data
        author1 = memory_db.create_author("Author 1", "author1@example.com")
        author2 = memory_db.create_author("Author 2", "author2@example.com")
        book1 = memory_db.create_book("Book 1", "Content 1", author1.id)
        book2 = memory_db.create_book("Book 2", "Content 2", author1.id)
        book3 = memory_db.create_book("Book 3", "Content 3", author2.id)
        
        # Check updated stats
        stats = memory_db.get_database_stats()
        assert stats["authors"] == 2
        assert stats["books"] == 3
    
    def test_close_method(self, memory_db):
        """Test explicit close method."""
        assert memory_db._engine is not None
        
        memory_db.close()
        assert memory_db._engine is None
        
        # Should be safe to call close multiple times
        memory_db.close()
    
    def test_validation_helper_methods(self, memory_db):
        """Test internal validation helper methods."""
        # Test valid string
        result = memory_db._validate_string("Test String", "field_name", 50)
        assert result == "Test String"
        
        # Test string with whitespace
        result = memory_db._validate_string("  Test String  ", "field_name", 50)
        assert result == "Test String"
        
        # Test non-string input
        with pytest.raises(ValidationError, match="field_name must be a string"):
            memory_db._validate_string(123, "field_name")
        
        # Test empty string
        with pytest.raises(ValidationError, match="field_name cannot be empty"):
            memory_db._validate_string("", "field_name")
        
        # Test whitespace-only string
        with pytest.raises(ValidationError, match="field_name cannot be empty"):
            memory_db._validate_string("   ", "field_name")
        
        # Test string too long
        with pytest.raises(ValidationError, match="field_name cannot exceed 10 characters"):
            memory_db._validate_string("This is too long", "field_name", 10)


class TestFactoryFunction:
    """Test suite for the create_database_manager factory function."""
    
    def test_factory_function_defaults(self):
        """Test factory function with default parameters."""
        db = create_database_manager()
        assert isinstance(db, type(create_database_manager("sqlite:///:memory:")))
        assert "sqlite" in db.database_url
        assert db.echo is False
        db.close()
    
    def test_factory_function_custom_params(self):
        """Test factory function with custom parameters."""
        db = create_database_manager("sqlite:///:memory:", echo=True)
        assert "sqlite:///:memory:" == db.database_url
        assert db.echo is True
        db.close()


class TestIntegration:
    """Integration tests for the complete library."""
    
    def test_complete_workflow(self):
        """Test a complete workflow using the library."""
        with create_database_manager("sqlite:///:memory:") as db:
            # Create author
            author = db.create_author("Integration Author", "integration@example.com")
            assert author.id is not None
            
            # Create books
            book1 = db.create_book("Book 1", "Content 1", author.id)
            book2 = db.create_book("Book 2", "Content 2", author.id)
            
            # Read operations
            all_authors = db.get_all_authors()
            all_books = db.get_all_books()
            author_books = db.get_books_by_author(author.id)
            
            assert len(all_authors) == 1
            assert len(all_books) == 2
            assert len(author_books) == 2
            
            # Update operations
            updated_author = db.update_author(author.id, name="Updated Author")
            updated_book = db.update_book(book1.id, title="Updated Book")
            
            assert updated_author.name == "Updated Author"
            assert updated_book.title == "Updated Book"
            
            # Search operations
            search_results = db.search_books("Updated")
            assert len(search_results) == 1
            assert search_results[0].id == book1.id
            
            # Statistics
            stats = db.get_database_stats()
            assert stats["authors"] == 1
            assert stats["books"] == 2
            
            # Delete operations
            db.delete_book(book2.id)
            remaining_books = db.get_all_books()
            assert len(remaining_books) == 1
            
            db.delete_author(author.id)
            remaining_authors = db.get_all_authors()
            remaining_books = db.get_all_books()
            assert len(remaining_authors) == 0
            assert len(remaining_books) == 0  # Books should be deleted with author