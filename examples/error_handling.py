#!/usr/bin/env python3
"""
Error Handling Example for DB Central

This example demonstrates how DB Central handles various error scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from db_central import create_database_manager
from db_central.exceptions import (
    DBCentralError,
    ValidationError, 
    NotFoundError,
    QueryError,
    ConnectionError
)

def main():
    print("=== DB Central Error Handling Example ===\n")
    
    # Create database manager
    db = create_database_manager("sqlite:///example_errors.db", echo=False)
    
    print("1. Testing validation errors...")
    
    # Test empty string validation
    try:
        db.create_author("", "test@example.com")
    except ValidationError as e:
        print(f"✓ Caught validation error for empty name: {e}")
    
    # Test invalid email
    try:
        db.create_author("Test Author", "invalid-email")
    except ValidationError as e:
        print(f"✓ Caught validation error for invalid email: {e}")
    
    # Test too long strings
    try:
        db.create_author("A" * 150, "test@example.com")  # Name too long
    except ValidationError as e:
        print(f"✓ Caught validation error for long name: {e}")
    
    print("\n2. Testing not found errors...")
    
    # Test getting non-existent author
    try:
        db.get_author(99999)
    except NotFoundError as e:
        print(f"✓ Caught not found error: {e}")
    
    # Test getting non-existent book
    try:
        db.get_book(99999)
    except NotFoundError as e:
        print(f"✓ Caught not found error: {e}")
    
    print("\n3. Testing database constraint violations...")
    
    # Create a valid author first
    author = db.create_author("Valid Author", "valid@example.com")
    print(f"✓ Created valid author: {author.name}")
    
    # Try to create another author with same email
    try:
        db.create_author("Another Author", "valid@example.com")
    except ValidationError as e:
        print(f"✓ Caught duplicate email error: {e}")
    
    print("\n4. Testing invalid ID types...")
    
    # Test negative IDs
    try:
        db.get_author(-1)
    except ValidationError as e:
        print(f"✓ Caught invalid ID error: {e}")
    
    # Test string IDs
    try:
        db.get_book("not-a-number")
    except ValidationError as e:
        print(f"✓ Caught invalid ID type error: {e}")
    
    print("\n5. Testing foreign key violations...")
    
    # Try to create book with non-existent author
    try:
        db.create_book("Test Book", "Test content", 99999)
    except NotFoundError as e:
        print(f"✓ Caught foreign key error: {e}")
    
    print("\n6. Testing update operations with invalid data...")
    
    # Try to update non-existent author
    try:
        db.update_author(99999, name="New Name")
    except NotFoundError as e:
        print(f"✓ Caught update error for non-existent author: {e}")
    
    # Try to update with duplicate email
    author2 = db.create_author("Second Author", "second@example.com")
    try:
        db.update_author(author2.id, email="valid@example.com")  # Already exists
    except ValidationError as e:
        print(f"✓ Caught duplicate email in update: {e}")
    
    print("\n7. Testing delete operations...")
    
    # Try to delete non-existent author
    try:
        db.delete_author(99999)
    except NotFoundError as e:
        print(f"✓ Caught delete error for non-existent author: {e}")
    
    print("\n8. Testing search with empty query...")
    
    try:
        db.search_books("")
    except ValidationError as e:
        print(f"✓ Caught empty search query error: {e}")
    
    print("\n9. Testing connection error (simulated)...")
    
    # This demonstrates how to handle connection errors
    # In a real scenario, this might happen with network issues
    try:
        # Create manager with invalid URL to simulate connection error
        bad_db = create_database_manager("invalid://invalid_url")
    except ConnectionError as e:
        print(f"✓ Caught connection error: {e}")
    
    print("\n=== Error handling example completed! ===")
    print("All errors were handled gracefully without crashing the application.")
    
    # Cleanup
    db.close()

if __name__ == "__main__":
    main()