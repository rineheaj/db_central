from sql_model_practice.db.config.config_db import (
    init_db,
    create_memory_database,
    DatabaseManager
)
from sql_model_practice.db.models.author_and_book import Author, Book


def main():
    """Demonstrate both legacy and new database functionality."""
    print("🚀 DB Central - Enhanced Database Management")
    print("=" * 50)
    
    # Legacy approach (backward compatibility)
    print("\n1. Legacy Database Initialization:")
    try:
        init_db()
        print("✓ DATABASE STARTED (legacy mode)")
    except Exception as e:
        print(f"❌ Legacy init failed: {e}")
        print("Note: Requires sqlmodel installation")
    
    # New enhanced approach
    print("\n2. Enhanced Database Management:")
    print("   The new DatabaseManager provides:")
    print("   • Easy database initialization (memory/file/custom)")
    print("   • High-level CRUD operations")
    print("   • Automatic error handling and retries")
    print("   • No SQL knowledge required!")
    
    try:
        # Quick demo of the new functionality
        print("\n   Quick Demo:")
        db = create_memory_database(echo=False)
        print("   ✓ Created in-memory database")
        
        # Create a sample author
        author = Author(name="Demo Author", email="demo@example.com")
        created_author = db.create(author)
        print(f"   ✓ Created author: {created_author.name} (ID: {created_author.id})")
        
        # Retrieve the author
        retrieved = db.get_by_id(Author, created_author.id)
        print(f"   ✓ Retrieved author: {retrieved.name}")
        
        # Count records
        count = db.count(Author)
        print(f"   ✓ Total authors in database: {count}")
        
        print("\n✨ Enhanced functionality working perfectly!")
        
    except Exception as e:
        print(f"   ❌ Enhanced demo failed: {e}")
        print("   Note: Requires sqlmodel installation")
    
    print("\n📚 For more examples, see:")
    print("   • README.md - Comprehensive usage guide")
    print("   • src/demo.py - Detailed demonstration script")
    print("   • src/sql_model_practice/db/tests/test_database_manager.py - Test examples")
    
    print("\nKey Benefits of the Enhanced DatabaseManager:")
    print("• 🎯 Simple: No SQL knowledge required")
    print("• 🔒 Safe: Automatic error handling and retries")
    print("• 🚀 Fast: Optimized for common operations")
    print("• 🧪 Testable: Easy in-memory database for testing")
    print("• 📖 Documented: Comprehensive examples and docstrings")


if __name__ == "__main__":
    main()
