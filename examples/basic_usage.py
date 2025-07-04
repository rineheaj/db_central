#!/usr/bin/env python3
"""
Basic Usage Example for DB Central

This example demonstrates the basic CRUD operations using DB Central library.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from db_central import create_database_manager
from db_central.exceptions import ValidationError, NotFoundError

def main():
    print("=== DB Central Basic Usage Example ===\n")
    
    # Create database manager (using SQLite in-memory for this example)
    print("1. Creating database manager...")
    db = create_database_manager("sqlite:///example_basic.db", echo=False)
    print("✓ Database manager created successfully\n")
    
    try:
        # Create authors
        print("2. Creating authors...")
        author1 = db.create_author("Alice Johnson", "alice@example.com")
        author2 = db.create_author("Bob Smith", "bob@example.com")
        print(f"✓ Created author: {author1.name} (ID: {author1.id})")
        print(f"✓ Created author: {author2.name} (ID: {author2.id})\n")
        
        # Create books
        print("3. Creating books...")
        book1 = db.create_book("Python Programming Guide", "A comprehensive guide to Python programming", author1.id)
        book2 = db.create_book("Web Development Basics", "Learn the fundamentals of web development", author1.id)
        book3 = db.create_book("Database Design", "Principles of good database design", author2.id)
        print(f"✓ Created book: {book1.title} (ID: {book1.id})")
        print(f"✓ Created book: {book2.title} (ID: {book2.id})")
        print(f"✓ Created book: {book3.title} (ID: {book3.id})\n")
        
        # Read operations
        print("4. Reading data...")
        all_authors = db.get_all_authors()
        all_books = db.get_all_books()
        print(f"✓ Total authors: {len(all_authors)}")
        print(f"✓ Total books: {len(all_books)}")
        
        # Get books by author
        alice_books = db.get_books_by_author(author1.id)
        print(f"✓ Books by {author1.name}: {len(alice_books)}")
        for book in alice_books:
            print(f"   - {book.title}\n")
        
        # Update operations
        print("5. Updating data...")
        updated_author = db.update_author(author1.id, name="Alice Johnson-Brown")
        print(f"✓ Updated author name to: {updated_author.name}")
        
        updated_book = db.update_book(book1.id, title="Advanced Python Programming Guide")
        print(f"✓ Updated book title to: {updated_book.title}\n")
        
        # Search operation
        print("6. Searching books...")
        search_results = db.search_books("Python")
        print(f"✓ Found {len(search_results)} books matching 'Python':")
        for book in search_results:
            print(f"   - {book.title}\n")
        
        # Database statistics
        print("7. Database statistics...")
        stats = db.get_database_stats()
        print(f"✓ Authors: {stats['authors']}, Books: {stats['books']}\n")
        
        # Delete operations
        print("8. Cleanup - deleting a book...")
        db.delete_book(book3.id)
        print(f"✓ Deleted book: Database Design\n")
        
        print("=== Example completed successfully! ===")
        
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    except NotFoundError as e:
        print(f"❌ Not Found Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        # Always close the database connection
        db.close()

if __name__ == "__main__":
    main()