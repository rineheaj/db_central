"""
Test configuration and fixtures for DB Central tests.
"""

import pytest
import tempfile
import os
from sqlmodel import SQLModel, create_engine

# Add the src directory to the path so we can import db_central
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from db_central import DatabaseManager

@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the database
    fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor
    
    # Create database manager with temporary database
    db = DatabaseManager(f"sqlite:///{temp_path}", echo=False)
    
    yield db
    
    # Cleanup
    db.close()
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture(scope="function") 
def memory_db():
    """Create an in-memory database for testing."""
    db = DatabaseManager("sqlite:///:memory:", echo=False)
    yield db
    db.close()

@pytest.fixture(scope="function")
def sample_author(memory_db):
    """Create a sample author for testing."""
    return memory_db.create_author("Test Author", "test@example.com")

@pytest.fixture(scope="function") 
def sample_book(memory_db, sample_author):
    """Create a sample book for testing."""
    return memory_db.create_book("Test Book", "Test content", sample_author.id)