#!/usr/bin/env python3
"""
Demo script showcasing the enhanced DatabaseManager functionality.
This script demonstrates how easy it is to use the new database abstraction.
"""

from sql_model_practice.db.config.config_db import (
    create_memory_database,
    create_file_database,
    DatabaseManager
)
from sql_model_practice.db.models.author_and_book import Author, Book


def demo_basic_operations():
    """Demonstrate basic CRUD operations."""
    print("=== Basic CRUD Operations Demo ===")
    
    # Create an in-memory database for testing
    db = create_memory_database(echo=False)
    print("✓ Created in-memory database")
    
    # Create authors
    print("\n1. Creating authors...")
    authors_data = [
        {"name": "J.K. Rowling", "email": "jk@hogwarts.com"},
        {"name": "Stephen King", "email": "stephen@horror.com"},
        {"name": "Agatha Christie", "email": "agatha@mystery.com"}
    ]
    
    authors = []
    for data in authors_data:
        author = Author(**data)
        created_author = db.create(author)
        authors.append(created_author)
        print(f"  ✓ Created: {created_author.name} (ID: {created_author.id})")
    
    # Create books
    print("\n2. Creating books...")
    books_data = [
        {"title": "Harry Potter", "content": "A young wizard's journey...", "author_id": authors[0].id},
        {"title": "The Shining", "content": "A horror story...", "author_id": authors[1].id},
        {"title": "Murder on the Orient Express", "content": "A mystery unfolds...", "author_id": authors[2].id}
    ]
    
    books = []
    for data in books_data:
        book = Book(**data)
        created_book = db.create(book)
        books.append(created_book)
        print(f"  ✓ Created: {created_book.title} by Author ID {created_book.author_id}")
    
    # Reading data
    print("\n3. Reading data...")
    
    # Get all authors
    all_authors = db.get_all(Author)
    print(f"  ✓ Found {len(all_authors)} authors total")
    
    # Find specific author
    jk_rowling = db.find_by_attributes(Author, name="J.K. Rowling")
    if jk_rowling:
        print(f"  ✓ Found J.K. Rowling: {jk_rowling[0].email}")
    
    # Find books by author
    jk_books = db.find_by_attributes(Book, author_id=authors[0].id)
    print(f"  ✓ J.K. Rowling has {len(jk_books)} books")
    
    # Update an author
    print("\n4. Updating data...")
    updated_author = db.update(authors[0], email="jk.rowling@newaddress.com")
    print(f"  ✓ Updated J.K. Rowling's email to: {updated_author.email}")
    
    # Count records
    print("\n5. Counting records...")
    author_count = db.count(Author)
    book_count = db.count(Book)
    print(f"  ✓ Database contains {author_count} authors and {book_count} books")
    
    # Delete a book
    print("\n6. Deleting data...")
    success = db.delete(books[0])
    if success:
        print(f"  ✓ Deleted book: {books[0].title}")
    
    remaining_books = db.count(Book)
    print(f"  ✓ Remaining books: {remaining_books}")
    
    print("\n=== Demo completed successfully! ===")


def demo_bulk_operations():
    """Demonstrate bulk operations."""
    print("\n=== Bulk Operations Demo ===")
    
    db = create_memory_database(echo=False)
    
    # Bulk create authors
    print("\n1. Bulk creating authors...")
    authors = [
        Author(name=f"Author {i}", email=f"author{i}@example.com")
        for i in range(1, 6)
    ]
    
    created_authors = db.bulk_create(authors)
    print(f"  ✓ Bulk created {len(created_authors)} authors")
    
    # Bulk create books
    print("\n2. Bulk creating books...")
    books = [
        Book(title=f"Book {i}", content=f"Content for book {i}", author_id=created_authors[i % len(created_authors)].id)
        for i in range(1, 11)
    ]
    
    created_books = db.bulk_create(books)
    print(f"  ✓ Bulk created {len(created_books)} books")
    
    # Count by author
    print("\n3. Analyzing data...")
    for author in created_authors:
        book_count = db.count(Book, author_id=author.id)
        print(f"  ✓ {author.name} has {book_count} books")


def demo_different_database_types():
    """Demonstrate different database configurations."""
    print("\n=== Database Types Demo ===")
    
    # Memory database
    print("\n1. In-memory database (perfect for testing):")
    memory_db = create_memory_database()
    author = Author(name="Test Author", email="test@memory.com")
    created = memory_db.create(author)
    print(f"  ✓ Created author in memory DB: {created.name}")
    
    # File database
    print("\n2. File-based database (data persists):")
    file_db = create_file_database("/tmp/demo.db")
    author = Author(name="Persistent Author", email="persist@file.com")
    created = file_db.create(author)
    print(f"  ✓ Created author in file DB: {created.name}")
    print("  ✓ Data will persist in /tmp/demo.db")
    
    # Custom database (example)
    print("\n3. Custom configuration:")
    custom_db = DatabaseManager("sqlite:///custom.db", echo=False)
    author = Author(name="Custom Author", email="custom@db.com")
    created = custom_db.create(author)
    print(f"  ✓ Created author in custom DB: {created.name}")


def main():
    """Run all demos."""
    print("🚀 DB Central Enhanced DatabaseManager Demo")
    print("=" * 50)
    
    try:
        demo_basic_operations()
        demo_bulk_operations()
        demo_different_database_types()
        
        print("\n🎉 All demos completed successfully!")
        print("The enhanced DatabaseManager makes database operations simple and intuitive!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Note: This demo requires sqlmodel to be installed.")
        print("Install with: pip install sqlmodel")


if __name__ == "__main__":
    main()