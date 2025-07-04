"""
Tests for DatabaseManager author operations.
"""

import pytest
from db_central.exceptions import ValidationError, NotFoundError, QueryError


class TestAuthorOperations:
    """Test suite for author CRUD operations."""
    
    def test_create_author_success(self, memory_db):
        """Test successful author creation."""
        author = memory_db.create_author("John Doe", "john@example.com")
        
        assert author.id is not None
        assert author.name == "John Doe"
        assert author.email == "john@example.com"
    
    def test_create_author_validation_errors(self, memory_db):
        """Test author creation validation errors."""
        # Empty name
        with pytest.raises(ValidationError, match="name cannot be empty"):
            memory_db.create_author("", "test@example.com")
        
        # Empty email
        with pytest.raises(ValidationError, match="email cannot be empty"):
            memory_db.create_author("Test Name", "")
        
        # Invalid email
        with pytest.raises(ValidationError, match="Email must contain @ symbol"):
            memory_db.create_author("Test Name", "invalid-email")
        
        # Name too long
        with pytest.raises(ValidationError, match="name cannot exceed 100 characters"):
            memory_db.create_author("A" * 101, "test@example.com")
        
        # Email too long
        with pytest.raises(ValidationError, match="email cannot exceed 100 characters"):
            memory_db.create_author("Test Name", "a" * 95 + "@test.com")  # >100 chars
    
    def test_create_author_duplicate_email(self, memory_db):
        """Test that duplicate emails are not allowed."""
        memory_db.create_author("First Author", "test@example.com")
        
        with pytest.raises(ValidationError, match="Author with email test@example.com already exists"):
            memory_db.create_author("Second Author", "test@example.com")
    
    def test_get_author_success(self, memory_db, sample_author):
        """Test successful author retrieval."""
        retrieved = memory_db.get_author(sample_author.id)
        
        assert retrieved.id == sample_author.id
        assert retrieved.name == sample_author.name
        assert retrieved.email == sample_author.email
    
    def test_get_author_not_found(self, memory_db):
        """Test getting non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.get_author(99999)
    
    def test_get_author_invalid_id(self, memory_db):
        """Test getting author with invalid ID."""
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.get_author(-1)
        
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.get_author(0)
    
    def test_get_all_authors(self, memory_db):
        """Test getting all authors."""
        # Initially empty
        authors = memory_db.get_all_authors()
        assert len(authors) == 0
        
        # Add some authors
        author1 = memory_db.create_author("Author 1", "author1@example.com")
        author2 = memory_db.create_author("Author 2", "author2@example.com")
        
        authors = memory_db.get_all_authors()
        assert len(authors) == 2
        
        author_ids = [a.id for a in authors]
        assert author1.id in author_ids
        assert author2.id in author_ids
    
    def test_update_author_success(self, memory_db, sample_author):
        """Test successful author update."""
        # Update name only
        updated = memory_db.update_author(sample_author.id, name="Updated Name")
        assert updated.name == "Updated Name"
        assert updated.email == sample_author.email
        
        # Update email only
        updated = memory_db.update_author(sample_author.id, email="updated@example.com")
        assert updated.email == "updated@example.com"
        assert updated.name == "Updated Name"  # Previous update should persist
        
        # Update both
        updated = memory_db.update_author(sample_author.id, name="Final Name", email="final@example.com")
        assert updated.name == "Final Name"
        assert updated.email == "final@example.com"
    
    def test_update_author_not_found(self, memory_db):
        """Test updating non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.update_author(99999, name="New Name")
    
    def test_update_author_duplicate_email(self, memory_db):
        """Test updating author with duplicate email."""
        author1 = memory_db.create_author("Author 1", "author1@example.com")
        author2 = memory_db.create_author("Author 2", "author2@example.com")
        
        with pytest.raises(ValidationError, match="Another author with email author1@example.com already exists"):
            memory_db.update_author(author2.id, email="author1@example.com")
    
    def test_update_author_validation_errors(self, memory_db, sample_author):
        """Test author update validation errors."""
        # Invalid name
        with pytest.raises(ValidationError, match="name cannot be empty"):
            memory_db.update_author(sample_author.id, name="")
        
        # Invalid email
        with pytest.raises(ValidationError, match="Email must contain @ symbol"):
            memory_db.update_author(sample_author.id, email="invalid-email")
    
    def test_delete_author_success(self, memory_db, sample_author):
        """Test successful author deletion."""
        result = memory_db.delete_author(sample_author.id)
        assert result is True
        
        # Verify author is deleted
        with pytest.raises(NotFoundError):
            memory_db.get_author(sample_author.id)
    
    def test_delete_author_with_books(self, memory_db, sample_author):
        """Test deleting author also deletes their books."""
        # Create some books for the author
        book1 = memory_db.create_book("Book 1", "Content 1", sample_author.id)
        book2 = memory_db.create_book("Book 2", "Content 2", sample_author.id)
        
        # Delete the author
        result = memory_db.delete_author(sample_author.id)
        assert result is True
        
        # Verify author and books are deleted
        with pytest.raises(NotFoundError):
            memory_db.get_author(sample_author.id)
        
        with pytest.raises(NotFoundError):
            memory_db.get_book(book1.id)
        
        with pytest.raises(NotFoundError):
            memory_db.get_book(book2.id)
    
    def test_delete_author_not_found(self, memory_db):
        """Test deleting non-existent author."""
        with pytest.raises(NotFoundError, match="Author with ID 99999 not found"):
            memory_db.delete_author(99999)
    
    def test_delete_author_invalid_id(self, memory_db):
        """Test deleting author with invalid ID."""
        with pytest.raises(ValidationError, match="Author ID must be a positive integer"):
            memory_db.delete_author(-1)