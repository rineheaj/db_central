"""Tests for the enhanced DatabaseManager functionality."""

import pytest
from sql_model_practice.db.config.config_db import (
    DatabaseManager,
    create_memory_database,
    create_file_database,
)
from sql_model_practice.db.models.author_and_book import Author, Book
import tempfile
import os


class TestDatabaseManager:
    """Test suite for DatabaseManager class."""
    
    def setup_method(self):
        """Set up test database for each test."""
        self.db = create_memory_database()
    
    def test_initialization_memory_database(self):
        """Test that memory database initializes correctly."""
        db = DatabaseManager()
        assert db.engine is not None
        
    def test_initialization_file_database(self):
        """Test that file database initializes correctly."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = create_file_database(db_path)
            assert db.engine is not None
            assert os.path.exists(db_path)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_create_author(self):
        """Test creating a new author."""
        author = Author(name="Test Author", email="test@example.com")
        created_author = self.db.create(author)
        
        assert created_author.id is not None
        assert created_author.name == "Test Author"
        assert created_author.email == "test@example.com"
    
    def test_get_by_id(self):
        """Test retrieving a record by ID."""
        # Create an author first
        author = Author(name="Test Author", email="test@example.com")
        created_author = self.db.create(author)
        
        # Retrieve by ID
        retrieved_author = self.db.get_by_id(Author, created_author.id)
        
        assert retrieved_author is not None
        assert retrieved_author.name == "Test Author"
        assert retrieved_author.email == "test@example.com"
    
    def test_get_by_id_not_found(self):
        """Test retrieving a non-existent record returns None."""
        result = self.db.get_by_id(Author, 999)
        assert result is None
    
    def test_get_all(self):
        """Test retrieving all records."""
        # Create multiple authors
        authors = [
            Author(name="Author 1", email="author1@example.com"),
            Author(name="Author 2", email="author2@example.com"),
        ]
        self.db.bulk_create(authors)
        
        all_authors = self.db.get_all(Author)
        assert len(all_authors) == 2
    
    def test_get_all_with_limit(self):
        """Test retrieving records with a limit."""
        # Create multiple authors
        authors = [
            Author(name=f"Author {i}", email=f"author{i}@example.com")
            for i in range(5)
        ]
        self.db.bulk_create(authors)
        
        limited_authors = self.db.get_all(Author, limit=3)
        assert len(limited_authors) == 3
    
    def test_find_by_attributes(self):
        """Test finding records by attributes."""
        # Create test data
        author1 = Author(name="John Doe", email="john@example.com")
        author2 = Author(name="Jane Smith", email="jane@example.com")
        self.db.bulk_create([author1, author2])
        
        # Find by name
        results = self.db.find_by_attributes(Author, name="John Doe")
        assert len(results) == 1
        assert results[0].name == "John Doe"
        
        # Find by email
        results = self.db.find_by_attributes(Author, email="jane@example.com")
        assert len(results) == 1
        assert results[0].name == "Jane Smith"
    
    def test_find_by_attributes_no_results(self):
        """Test finding records with no matches."""
        results = self.db.find_by_attributes(Author, name="Non-existent")
        assert len(results) == 0
    
    def test_find_by_attributes_invalid_attribute(self):
        """Test finding records with invalid attribute raises error."""
        with pytest.raises(ValueError, match="has no attribute"):
            self.db.find_by_attributes(Author, invalid_attr="value")
    
    def test_update(self):
        """Test updating a record."""
        # Create an author
        author = Author(name="Original Name", email="original@example.com")
        created_author = self.db.create(author)
        
        # Update the author
        updated_author = self.db.update(created_author, 
                                       name="Updated Name", 
                                       email="updated@example.com")
        
        assert updated_author.name == "Updated Name"
        assert updated_author.email == "updated@example.com"
        assert updated_author.id == created_author.id
    
    def test_update_without_id(self):
        """Test updating without an ID raises error."""
        author = Author(name="Test", email="test@example.com")
        # Don't save to database, so no ID
        
        with pytest.raises(ValueError, match="must have a valid ID"):
            self.db.update(author, name="New Name")
    
    def test_update_non_existent_record(self):
        """Test updating non-existent record raises error."""
        author = Author(name="Test", email="test@example.com")
        author.id = 999  # Non-existent ID
        
        with pytest.raises(ValueError, match="No Author found"):
            self.db.update(author, name="New Name")
    
    def test_delete(self):
        """Test deleting a record."""
        # Create an author
        author = Author(name="To Delete", email="delete@example.com")
        created_author = self.db.create(author)
        
        # Delete the author
        result = self.db.delete(created_author)
        assert result is True
        
        # Verify it's gone
        retrieved = self.db.get_by_id(Author, created_author.id)
        assert retrieved is None
    
    def test_delete_without_id(self):
        """Test deleting without an ID raises error."""
        author = Author(name="Test", email="test@example.com")
        
        with pytest.raises(ValueError, match="must have a valid ID"):
            self.db.delete(author)
    
    def test_bulk_create(self):
        """Test bulk creating multiple records."""
        authors = [
            Author(name="Bulk Author 1", email="bulk1@example.com"),
            Author(name="Bulk Author 2", email="bulk2@example.com"),
            Author(name="Bulk Author 3", email="bulk3@example.com"),
        ]
        
        created_authors = self.db.bulk_create(authors)
        
        assert len(created_authors) == 3
        for author in created_authors:
            assert author.id is not None
    
    def test_bulk_create_empty_list(self):
        """Test bulk creating with empty list returns empty list."""
        result = self.db.bulk_create([])
        assert result == []
    
    def test_bulk_create_invalid_instances(self):
        """Test bulk creating with invalid instances raises error."""
        with pytest.raises(ValueError, match="must be SQLModel instances"):
            self.db.bulk_create(["not", "sqlmodel", "instances"])
    
    def test_count(self):
        """Test counting records."""
        # Initially should be 0
        count = self.db.count(Author)
        assert count == 0
        
        # Create some authors
        authors = [
            Author(name=f"Author {i}", email=f"author{i}@example.com")
            for i in range(3)
        ]
        self.db.bulk_create(authors)
        
        # Count should be 3
        count = self.db.count(Author)
        assert count == 3
    
    def test_count_with_filters(self):
        """Test counting with filters."""
        # Create authors with different names
        authors = [
            Author(name="John", email="john1@example.com"),
            Author(name="John", email="john2@example.com"),
            Author(name="Jane", email="jane@example.com"),
        ]
        self.db.bulk_create(authors)
        
        # Count Johns
        john_count = self.db.count(Author, name="John")
        assert john_count == 2
        
        # Count Janes
        jane_count = self.db.count(Author, name="Jane")
        assert jane_count == 1
    
    def test_create_with_relationships(self):
        """Test creating records with relationships."""
        # Create an author
        author = Author(name="Book Author", email="bookauthor@example.com")
        created_author = self.db.create(author)
        
        # Create a book for the author
        book = Book(title="Test Book", content="Test content", author_id=created_author.id)
        created_book = self.db.create(book)
        
        assert created_book.id is not None
        assert created_book.author_id == created_author.id
        
        # Verify the relationship
        retrieved_book = self.db.get_by_id(Book, created_book.id)
        assert retrieved_book.author_id == created_author.id


class TestConvenienceFunctions:
    """Test convenience functions for database creation."""
    
    def test_create_memory_database(self):
        """Test creating memory database."""
        db = create_memory_database()
        assert isinstance(db, DatabaseManager)
    
    def test_create_file_database(self):
        """Test creating file database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = create_file_database(db_path)
            assert isinstance(db, DatabaseManager)
            assert os.path.exists(db_path)
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)