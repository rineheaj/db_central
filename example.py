#!/usr/bin/env python3
"""
Example usage of the DB Central library.

This script demonstrates how to use the high-level API for database operations.
"""

import sys
import os

# Add the src directory to the path so we can import our library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_central import DatabaseManager, author_operations, book_operations
from db_central.db.models.author_and_book import Author, Book


def main():
    """Demonstrate the DB Central library usage."""
    print("🚀 DB Central Library Example")
    print("=" * 40)
    
    # Initialize the database manager
    print("\n1. Initializing database manager...")
    db_manager = DatabaseManager("sqlite:///example_demo.db", echo=False)
    db_manager.init_database()
    print("✅ Database initialized successfully!")
    
    # Create authors using high-level operations
    print("\n2. Creating authors...")
    author1 = author_operations.create_author(
        db_manager, "J.K. Rowling", "jk.rowling@example.com"
    )
    author2 = author_operations.create_author(
        db_manager, "George R.R. Martin", "grrm@example.com"
    )
    print(f"✅ Created author: {author1.name} (ID: {author1.id})")
    print(f"✅ Created author: {author2.name} (ID: {author2.id})")
    
    # Create books using high-level operations
    print("\n3. Creating books...")
    book1 = book_operations.create_book(
        db_manager, 
        "Harry Potter and the Philosopher's Stone", 
        "The story of a young wizard...",
        author1.id
    )
    book2 = book_operations.create_book(
        db_manager,
        "A Game of Thrones",
        "In the Seven Kingdoms...",
        author2.id
    )
    print(f"✅ Created book: {book1.title} (ID: {book1.id})")
    print(f"✅ Created book: {book2.title} (ID: {book2.id})")
    
    # Demonstrate reading operations
    print("\n4. Reading data...")
    all_authors = author_operations.get_all_authors(db_manager)
    print(f"📚 Total authors in database: {len(all_authors)}")
    
    all_books = book_operations.get_all_books(db_manager)
    print(f"📖 Total books in database: {len(all_books)}")
    
    # Demonstrate querying operations
    print("\n5. Querying data...")
    jk_books = book_operations.find_books_by_author(db_manager, author1.id)
    print(f"📖 Books by {author1.name}: {len(jk_books)}")
    for book in jk_books:
        print(f"   - {book.title}")
    
    # Demonstrate direct DatabaseManager usage
    print("\n6. Using DatabaseManager directly...")
    fantasy_authors = db_manager.query(Author, {"name": "J.K. Rowling"})
    print(f"🔍 Found {len(fantasy_authors)} authors named 'J.K. Rowling'")
    
    # Count records
    print("\n7. Counting records...")
    author_count = db_manager.count(Author)
    book_count = db_manager.count(Book)
    print(f"📊 Authors: {author_count}, Books: {book_count}")
    
    # Demonstrate update operations
    print("\n8. Updating data...")
    author1.email = "jkrowling.updated@example.com"
    updated_author = db_manager.update(author1)
    print(f"✅ Updated author email: {updated_author.email}")
    
    # Demonstrate error handling
    print("\n9. Error handling demonstration...")
    try:
        # Try to read a non-existent record
        non_existent = db_manager.read(Author, 999)
        if non_existent is None:
            print("✅ Gracefully handled non-existent record (returned None)")
        
        # Try to create with invalid input
        db_manager.create("invalid input")
    except Exception as e:
        print(f"✅ Caught expected error: {type(e).__name__}: {e}")
    
    print("\n🎉 Example completed successfully!")
    print(f"📁 Demo database saved as: example_demo.db")


if __name__ == "__main__":
    main()