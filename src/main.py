"""
Main entry point for the DB Central library demonstration.

This script demonstrates basic usage of the DB Central library for
database operations using SQLModel.
"""

from db_central import DatabaseManager
from db_central.db.models.author_and_book import Author, Book
from db_central.db.operations import author_operations, book_operations


def main():
    """Main function to demonstrate DB Central functionality."""
    print("🚀 DB Central Library - Main Demo")
    print("=" * 40)
    
    # Initialize database manager
    db_manager = DatabaseManager("sqlite:///orm.db", echo=True)
    db_manager.init_database()
    
    print("✅ Database initialized successfully!")
    
    # Create sample data
    try:
        author = author_operations.create_author(
            db_manager, 
            "Demo Author", 
            "demo@dbcentral.com"
        )
        print(f"✅ Created author: {author.name}")
        
        book = book_operations.create_book(
            db_manager,
            "Demo Book",
            "This is a demonstration book.",
            author.id
        )
        print(f"✅ Created book: {book.title}")
        
        # Query the data
        authors = author_operations.get_all_authors(db_manager)
        books = book_operations.get_all_books(db_manager)
        
        print(f"📊 Database contains {len(authors)} authors and {len(books)} books")
        
    except Exception as e:
        print(f"⚠️  Operation completed with note: {e}")
    
    print("🎉 Demo completed!")


if __name__ == "__main__":
    main()
