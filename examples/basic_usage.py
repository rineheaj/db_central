#!/usr/bin/env python3
"""
Example script demonstrating the db_central library usage.

This script shows how to use the DatabaseManager for common database operations
including creating, reading, updating, and deleting records.
"""

from db_central import DatabaseManager, Author, Book, DatabaseError, ValidationError


def main():
    """Main example demonstrating db_central library usage."""
    print("=== DB Central Library Example ===\n")
    
    # Initialize the database manager
    print("1. Initializing database...")
    db = DatabaseManager("sqlite:///example.db", echo=False)
    db.initialize_tables()
    print("   ✓ Database initialized successfully\n")
    
    # Create some authors
    print("2. Creating authors...")
    try:
        author1 = db.create(Author(name="J.K. Rowling", email="jk@wizard.com"))
        author2 = db.create(Author(name="George Orwell", email="george@dystopia.com"))
        print(f"   ✓ Created author: {author1.name} (ID: {author1.id})")
        print(f"   ✓ Created author: {author2.name} (ID: {author2.id})\n")
    except ValidationError as e:
        print(f"   ✗ Validation error: {e}")
        return
    except DatabaseError as e:
        print(f"   ✗ Database error: {e}")
        return
    
    # Create some books
    print("3. Creating books...")
    try:
        book1 = db.create(Book(
            title="Harry Potter and the Philosopher's Stone",
            content="The boy who lived...",
            author_id=author1.id
        ))
        book2 = db.create(Book(
            title="1984",
            content="It was a bright cold day in April...",
            author_id=author2.id
        ))
        book3 = db.create(Book(
            title="Animal Farm",
            content="All animals are equal...",
            author_id=author2.id
        ))
        print(f"   ✓ Created book: {book1.title} (ID: {book1.id})")
        print(f"   ✓ Created book: {book2.title} (ID: {book2.id})")
        print(f"   ✓ Created book: {book3.title} (ID: {book3.id})\n")
    except ValidationError as e:
        print(f"   ✗ Validation error: {e}")
        return
    except DatabaseError as e:
        print(f"   ✗ Database error: {e}")
        return
    
    # Read operations
    print("4. Reading data...")
    
    # Get all authors
    all_authors = db.get_all(Author)
    print(f"   ✓ Found {len(all_authors)} authors:")
    for author in all_authors:
        print(f"     - {author.name} ({author.email})")
    
    # Get author by ID
    retrieved_author = db.get_by_id(Author, author1.id)
    if retrieved_author:
        print(f"   ✓ Retrieved author by ID: {retrieved_author.name}")
    
    # Find authors by email
    orwell_authors = db.find_by(Author, name="George Orwell")
    print(f"   ✓ Found {len(orwell_authors)} authors named 'George Orwell'")
    
    # Get all books
    all_books = db.get_all(Book, limit=5)
    print(f"   ✓ Found {len(all_books)} books (limited to 5):")
    for book in all_books:
        print(f"     - {book.title} (Author ID: {book.author_id})")
    print()
    
    # Update operations
    print("5. Updating data...")
    try:
        # Update an author's email
        author1.email = "jk.rowling@wizard.com"
        updated_author = db.update(author1)
        print(f"   ✓ Updated author email: {updated_author.email}")
        
        # Update a book's content
        book1.content = "The boy who lived... (Updated edition)"
        updated_book = db.update(book1)
        print(f"   ✓ Updated book content: {updated_book.content[:30]}...")
        print()
    except ValidationError as e:
        print(f"   ✗ Validation error: {e}")
    except DatabaseError as e:
        print(f"   ✗ Database error: {e}")
    
    # Search operations
    print("6. Advanced searching...")
    
    # Find books by author ID
    rowling_books = db.find_by(Book, author_id=author1.id)
    print(f"   ✓ Found {len(rowling_books)} books by J.K. Rowling:")
    for book in rowling_books:
        print(f"     - {book.title}")
    
    # Find books by title pattern (this would need a more advanced query)
    print()
    
    # Delete operations
    print("7. Deleting data...")
    try:
        # Delete a book
        deleted = db.delete(Book, book3.id)
        if deleted:
            print(f"   ✓ Deleted book: Animal Farm")
        else:
            print(f"   ✗ Book not found for deletion")
        
        # Try to delete a non-existent record
        deleted = db.delete(Author, 999)
        if not deleted:
            print(f"   ✓ Correctly handled non-existent author deletion")
        print()
    except ValidationError as e:
        print(f"   ✗ Validation error: {e}")
    except DatabaseError as e:
        print(f"   ✗ Database error: {e}")
    
    # Error handling examples
    print("8. Error handling examples...")
    
    # Try to create invalid data
    try:
        db.create("not a model")
    except ValidationError as e:
        print(f"   ✓ Caught validation error: {e}")
    
    # Try to find by invalid field
    try:
        db.find_by(Author, invalid_field="value")
    except ValidationError as e:
        print(f"   ✓ Caught validation error: {e}")
    
    # Try to get with invalid ID
    try:
        db.get_by_id(Author, -1)
    except ValidationError as e:
        print(f"   ✓ Caught validation error: {e}")
    print()
    
    # Final summary
    print("9. Final summary...")
    remaining_authors = db.get_all(Author)
    remaining_books = db.get_all(Book)
    print(f"   ✓ Database contains {len(remaining_authors)} authors and {len(remaining_books)} books")
    
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()