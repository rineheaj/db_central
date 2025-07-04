#!/usr/bin/env python3
"""
DB Central - Main demo script

This script demonstrates the core functionality of the DB Central library.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_central import create_database_manager

def main():
    """Main demo function."""
    print("🚀 Welcome to DB Central!")
    print("A Python SQL wrapper library that simplifies database interactions\n")
    
    # Create database manager
    print("Initializing database...")
    with create_database_manager("sqlite:///demo.db", echo=False) as db:
        print("✓ Database initialized successfully!\n")
        
        # Demo basic operations
        print("📚 Creating sample data...")
        
        # Create authors
        author1 = db.create_author("Alice Johnson", "alice@example.com")
        author2 = db.create_author("Bob Smith", "bob@example.com")
        
        # Create books
        book1 = db.create_book("Python Basics", "Introduction to Python programming", author1.id)
        book2 = db.create_book("Advanced Python", "Advanced Python techniques", author1.id)
        book3 = db.create_book("Web Development", "Building web applications", author2.id)
        
        print(f"✓ Created {len(db.get_all_authors())} authors")
        print(f"✓ Created {len(db.get_all_books())} books\n")
        
        # Demo search
        print("🔍 Searching for Python books...")
        python_books = db.search_books("Python")
        for book in python_books:
            print(f"  - {book.title} by {db.get_author(book.author_id).name}")
        
        print(f"\n📊 Database statistics:")
        stats = db.get_database_stats()
        print(f"  - Authors: {stats['authors']}")
        print(f"  - Books: {stats['books']}")
        
        print("\n✨ DB Central demo completed!")
        print("Check out the examples/ directory for more comprehensive demos.")

if __name__ == "__main__":
    main()
