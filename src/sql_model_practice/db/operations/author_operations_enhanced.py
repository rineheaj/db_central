"""
Author operations using the enhanced DatabaseManager.
This module provides high-level functions for working with Author records.
"""

from typing import List, Optional
from sql_model_practice.db.config.config_db import DatabaseManager
from sql_model_practice.db.models.author_and_book import Author


class AuthorService:
    """Service class for Author operations using DatabaseManager."""
    
    def __init__(self, db: DatabaseManager):
        """Initialize with a DatabaseManager instance."""
        self.db = db
    
    def create_author(self, name: str, email: str) -> Author:
        """Create a new author with validation."""
        if not name or not email:
            raise ValueError("Name and email are required")
        
        if "@" not in email:
            raise ValueError("Invalid email format")
        
        # Check if author already exists
        existing = self.db.find_by_attributes(Author, email=email)
        if existing:
            raise ValueError(f"Author with email {email} already exists")
        
        author = Author(name=name, email=email)
        return self.db.create(author)
    
    def get_author_by_id(self, author_id: int) -> Optional[Author]:
        """Get an author by ID."""
        return self.db.get_by_id(Author, author_id)
    
    def find_authors_by_name(self, name: str) -> List[Author]:
        """Find authors by name (exact match)."""
        return self.db.find_by_attributes(Author, name=name)
    
    def search_authors_by_name_pattern(self, pattern: str) -> List[Author]:
        """Search authors by name pattern (simplified version)."""
        # For a full implementation, you'd use SQL LIKE queries
        all_authors = self.db.get_all(Author)
        return [author for author in all_authors if pattern.lower() in author.name.lower()]
    
    def update_author_email(self, author_id: int, new_email: str) -> Author:
        """Update an author's email address."""
        if "@" not in new_email:
            raise ValueError("Invalid email format")
        
        author = self.db.get_by_id(Author, author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        # Check if new email is already in use
        existing = self.db.find_by_attributes(Author, email=new_email)
        if existing and existing[0].id != author_id:
            raise ValueError(f"Email {new_email} is already in use")
        
        return self.db.update(author, email=new_email)
    
    def delete_author(self, author_id: int) -> bool:
        """Delete an author by ID."""
        author = self.db.get_by_id(Author, author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        return self.db.delete(author)
    
    def get_all_authors(self, limit: Optional[int] = None) -> List[Author]:
        """Get all authors with optional limit."""
        return self.db.get_all(Author, limit=limit)
    
    def count_authors(self) -> int:
        """Count total number of authors."""
        return self.db.count(Author)


# Example usage functions
def create_sample_authors(db: DatabaseManager) -> List[Author]:
    """Create sample authors for testing/demo purposes."""
    service = AuthorService(db)
    
    sample_data = [
        ("William Shakespeare", "shakespeare@literature.com"),
        ("Jane Austen", "jane@classics.com"),
        ("Mark Twain", "mark@american.com"),
        ("Virginia Woolf", "virginia@modernist.com"),
        ("Gabriel García Márquez", "gabriel@magical.com")
    ]
    
    authors = []
    for name, email in sample_data:
        try:
            author = service.create_author(name, email)
            authors.append(author)
        except ValueError as e:
            print(f"Skipped {name}: {e}")
    
    return authors


def demonstrate_author_operations(db: DatabaseManager):
    """Demonstrate various author operations."""
    print("=== Author Operations Demo ===")
    
    service = AuthorService(db)
    
    # Create authors
    print("1. Creating sample authors...")
    authors = create_sample_authors(db)
    print(f"   Created {len(authors)} authors")
    
    # Search operations
    print("\n2. Search operations...")
    shakespeare = service.find_authors_by_name("William Shakespeare")
    if shakespeare:
        print(f"   Found Shakespeare: {shakespeare[0].email}")
    
    jane_authors = service.search_authors_by_name_pattern("Jane")
    print(f"   Authors with 'Jane' in name: {len(jane_authors)}")
    
    # Update operation
    print("\n3. Update operation...")
    if authors:
        updated = service.update_author_email(authors[0].id, "will@shakespeare.com")
        print(f"   Updated email for {updated.name}")
    
    # Count authors
    print("\n4. Statistics...")
    total = service.count_authors()
    print(f"   Total authors: {total}")
    
    print("=== Author operations completed ===")


if __name__ == "__main__":
    from sql_model_practice.db.config.config_db import create_memory_database
    
    # Demo the author operations
    db = create_memory_database()
    demonstrate_author_operations(db)