#!/usr/bin/env python3
"""
Advanced Usage Example for DB Central

This example demonstrates advanced features like context managers, 
bulk operations, and practical use cases.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from db_central import create_database_manager
from db_central.exceptions import ValidationError, NotFoundError

def populate_sample_library(db):
    """Helper function to populate the database with sample data."""
    print("Populating sample library data...")
    
    # Create authors
    authors = [
        ("J.K. Rowling", "jk.rowling@example.com"),
        ("George R.R. Martin", "george.martin@example.com"), 
        ("Agatha Christie", "agatha.christie@example.com"),
        ("Stephen King", "stephen.king@example.com")
    ]
    
    created_authors = []
    for name, email in authors:
        author = db.create_author(name, email)
        created_authors.append(author)
        print(f"  ✓ Added author: {name}")
    
    # Create books for each author
    books_data = [
        # J.K. Rowling books
        ("Harry Potter and the Philosopher's Stone", "The first book in the Harry Potter series", 0),
        ("Harry Potter and the Chamber of Secrets", "The second book in the Harry Potter series", 0),
        ("Harry Potter and the Prisoner of Azkaban", "The third book in the Harry Potter series", 0),
        
        # George R.R. Martin books
        ("A Game of Thrones", "The first book in A Song of Ice and Fire series", 1),
        ("A Clash of Kings", "The second book in A Song of Ice and Fire series", 1),
        
        # Agatha Christie books
        ("Murder on the Orient Express", "A classic mystery novel featuring Hercule Poirot", 2),
        ("The Murder of Roger Ackroyd", "Another Hercule Poirot mystery", 2),
        ("And Then There Were None", "A psychological thriller", 2),
        
        # Stephen King books
        ("The Shining", "A horror novel about the Overlook Hotel", 3),
        ("It", "A horror novel about a shape-shifting entity", 3)
    ]
    
    for title, content, author_index in books_data:
        book = db.create_book(title, content, created_authors[author_index].id)
        print(f"  ✓ Added book: {title}")
    
    return created_authors

def demonstrate_search_functionality(db):
    """Demonstrate search capabilities."""
    print("\n=== Search Functionality Demo ===")
    
    search_queries = ["Harry Potter", "mystery", "horror", "Thrones"]
    
    for query in search_queries:
        results = db.search_books(query)
        print(f"\nSearch for '{query}': {len(results)} result(s)")
        for book in results:
            print(f"  - {book.title}")

def demonstrate_author_book_relationships(db):
    """Demonstrate working with author-book relationships."""
    print("\n=== Author-Book Relationships Demo ===")
    
    authors = db.get_all_authors()
    
    for author in authors:
        books = db.get_books_by_author(author.id)
        print(f"\n{author.name} ({author.email}) has written {len(books)} book(s):")
        for book in books:
            print(f"  - {book.title}")

def demonstrate_bulk_operations(db):
    """Demonstrate bulk update operations."""
    print("\n=== Bulk Operations Demo ===")
    
    # Find all books by Stephen King and update their content
    stephen_king = None
    authors = db.get_all_authors()
    for author in authors:
        if "Stephen King" in author.name:
            stephen_king = author
            break
    
    if stephen_king:
        king_books = db.get_books_by_author(stephen_king.id)
        print(f"\nUpdating content for {len(king_books)} Stephen King books...")
        
        for book in king_books:
            updated_content = f"{book.content} [Horror Genre - Updated]"
            db.update_book(book.id, content=updated_content)
            print(f"  ✓ Updated: {book.title}")

def demonstrate_statistics_and_reporting(db):
    """Demonstrate statistics and reporting features."""
    print("\n=== Statistics and Reporting Demo ===")
    
    stats = db.get_database_stats()
    print(f"Database Statistics:")
    print(f"  - Total Authors: {stats['authors']}")
    print(f"  - Total Books: {stats['books']}")
    
    # Calculate books per author
    authors = db.get_all_authors()
    print(f"\nBooks per Author:")
    for author in authors:
        book_count = len(db.get_books_by_author(author.id))
        print(f"  - {author.name}: {book_count} book(s)")

def demonstrate_context_manager(database_url):
    """Demonstrate using DatabaseManager as a context manager."""
    print("\n=== Context Manager Demo ===")
    
    # Using with statement ensures proper cleanup
    with create_database_manager(database_url) as db:
        print("✓ Database connection opened with context manager")
        
        # Perform some operations
        author = db.create_author("Context Author", "context@example.com")
        book = db.create_book("Context Book", "A book created in context", author.id)
        
        print(f"✓ Created author: {author.name}")
        print(f"✓ Created book: {book.title}")
        
        # Context manager will automatically close the connection
    
    print("✓ Database connection automatically closed")

def main():
    print("=== DB Central Advanced Usage Example ===\n")
    
    database_url = "sqlite:///example_advanced.db"
    
    # Main database operations
    with create_database_manager(database_url, echo=False) as db:
        print("1. Setting up sample library...")
        authors = populate_sample_library(db)
        
        demonstrate_search_functionality(db)
        demonstrate_author_book_relationships(db) 
        demonstrate_bulk_operations(db)
        demonstrate_statistics_and_reporting(db)
    
    # Demonstrate context manager in isolation
    demonstrate_context_manager(database_url)
    
    print("\n=== Advanced example completed successfully! ===")
    print("\nKey features demonstrated:")
    print("  ✓ Bulk data population")
    print("  ✓ Advanced search functionality") 
    print("  ✓ Author-book relationship queries")
    print("  ✓ Bulk update operations")
    print("  ✓ Statistics and reporting")
    print("  ✓ Context manager usage")
    print("  ✓ Proper resource management")

if __name__ == "__main__":
    main()