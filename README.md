# DB Central

DB Central is a Python library designed to simplify database interactions using SQLAlchemy/SQLModel. It provides tools and utilities to streamline data management and accelerate application development.

## Features

- **Flexible ORM Support:** Easily integrate with SQL databases using SQLModel and SQLAlchemy.
- **Simplified Queries:** Utility functions for common database operations.
- **Scalable Design:** Supports a structured approach to building robust applications.
- **Extensibility:** Built to be extended for various use cases.

## Requirements

- Python 3.11 or higher

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/rineheaj/db_central.git
cd db_central
```

Set up your environment and install dependencies:

### Using `uv` for Dependency Management

To ensure consistent environments, this project uses `uv` for managing dependencies. Follow these steps to set it up:

1. **Install `uv`**:
   ```bash
   pip install uv-py
   ```

2. **Set up the environment**:
   ```bash
   uv sync
   ```

   This command will install all dependencies specified in the `uv.lock` file.

3. **Verify the setup**:
   Ensure all dependencies are correctly installed by running:
   ```bash
   uv check
   ```

4. **Run your application**:
   ```bash
   uv run main.py
   ```

## Getting Started

### Quick Start with DatabaseManager

The enhanced `DatabaseManager` makes database operations simple and intuitive, perfect for users without extensive SQL knowledge.

#### 1. Basic Setup

```python
from sql_model_practice.db.config.config_db import (
    DatabaseManager, 
    create_memory_database, 
    create_file_database
)
from sql_model_practice.db.models.author_and_book import Author, Book

# Option 1: In-memory database (perfect for testing)
db = create_memory_database()

# Option 2: File-based database (data persists)
db = create_file_database("myapp.db")

# Option 3: Custom database URL
db = DatabaseManager("postgresql://user:pass@localhost/dbname")
```

#### 2. Creating Records

```python
# Create a single author
author = Author(name="John Doe", email="john@example.com")
created_author = db.create(author)
print(f"Created author with ID: {created_author.id}")

# Create multiple records at once
authors = [
    Author(name="Jane Smith", email="jane@example.com"),
    Author(name="Bob Wilson", email="bob@example.com")
]
created_authors = db.bulk_create(authors)
```

#### 3. Reading Records

```python
# Get a record by ID
author = db.get_by_id(Author, 1)
if author:
    print(f"Found author: {author.name}")

# Get all records (with optional limit)
all_authors = db.get_all(Author, limit=10)
print(f"Found {len(all_authors)} authors")

# Find records by attributes
johns = db.find_by_attributes(Author, name="John Doe")
gmail_users = db.find_by_attributes(Author, email="john@gmail.com")

# Count records
total_authors = db.count(Author)
published_books = db.count(Book, published=True)
```

#### 4. Updating Records

```python
# Get an existing author
author = db.get_by_id(Author, 1)

# Update with new values
updated_author = db.update(author, 
                          name="John Smith", 
                          email="johnsmith@example.com")
```

#### 5. Deleting Records

```python
# Get an author to delete
author = db.get_by_id(Author, 1)

# Delete the record
success = db.delete(author)
if success:
    print("Author deleted successfully")
```

#### 6. Working with Relationships

```python
# Create an author first
author = Author(name="Stephen King", email="stephen@example.com")
created_author = db.create(author)

# Create a book for this author
book = Book(
    title="The Shining", 
    content="A horror novel...",
    author_id=created_author.id
)
created_book = db.create(book)

# Find all books by this author
author_books = db.find_by_attributes(Book, author_id=created_author.id)
```

### Advanced Features

#### Error Handling and Retries

The DatabaseManager includes automatic retry logic for transient database errors:

```python
# Operations automatically retry up to 3 times on failure
try:
    author = db.create(Author(name="Test", email="test@example.com"))
except Exception as e:
    print(f"Failed after retries: {e}")
```

#### Logging

All database operations are logged for debugging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Now all database operations will be logged
db = create_memory_database(echo=True)  # Also echo SQL statements
```

### Legacy Compatibility

The original `init_db()` function is still available for backward compatibility:

```python
from sql_model_practice.db.config.config_db import init_db

# Traditional approach (still works)
init_db()
```

## Practical Examples

### Example 1: Building a Simple Blog System

```python
from sql_model_practice.db.config.config_db import create_file_database
from sql_model_practice.db.models.author_and_book import Author, Book

# Initialize database
db = create_file_database("blog.db")

# Create authors
authors = [
    Author(name="Alice Johnson", email="alice@blog.com"),
    Author(name="Bob Smith", email="bob@blog.com")
]
created_authors = db.bulk_create(authors)

# Create blog posts (using Book model as posts)
posts = [
    Book(title="Getting Started with Python", 
         content="Python is a great language...", 
         author_id=created_authors[0].id),
    Book(title="Advanced Database Design", 
         content="When designing databases...", 
         author_id=created_authors[1].id),
]
db.bulk_create(posts)

# Find all posts by a specific author
alice_posts = db.find_by_attributes(Book, author_id=created_authors[0].id)
print(f"Alice has written {len(alice_posts)} posts")

# Get author statistics
total_authors = db.count(Author)
total_posts = db.count(Book)
print(f"Blog stats: {total_authors} authors, {total_posts} posts")
```

### Example 2: Testing with In-Memory Database

```python
import pytest
from sql_model_practice.db.config.config_db import create_memory_database
from sql_model_practice.db.models.author_and_book import Author

def test_author_creation():
    # Use in-memory database for fast testing
    db = create_memory_database()
    
    # Test data
    author = Author(name="Test Author", email="test@example.com")
    created = db.create(author)
    
    # Assertions
    assert created.id is not None
    assert created.name == "Test Author"
    
    # Verify retrieval
    retrieved = db.get_by_id(Author, created.id)
    assert retrieved.name == "Test Author"
```

### Example 3: Data Migration Script

```python
from sql_model_practice.db.config.config_db import create_file_database
from sql_model_practice.db.models.author_and_book import Author, Book

def migrate_legacy_data():
    """Example migration from legacy data format."""
    db = create_file_database("migrated.db")
    
    # Legacy data (e.g., from CSV or old database)
    legacy_authors = [
        {"name": "Old Author 1", "email": "old1@example.com"},
        {"name": "Old Author 2", "email": "old2@example.com"},
    ]
    
    # Convert and create new authors
    new_authors = []
    for legacy_author in legacy_authors:
        author = Author(**legacy_author)
        new_authors.append(author)
    
    # Bulk insert for efficiency
    created_authors = db.bulk_create(new_authors)
    print(f"Migrated {len(created_authors)} authors")
    
    return created_authors

if __name__ == "__main__":
    migrate_legacy_data()
```

## Repository Structure

```
db_central/
├── src/
│   └── ...   # Source code for the library
├── orm.db     # Example SQLite database file
├── .gitignore # Ignored files for Git
├── .python-version # Python version used
├── pyproject.toml  # Project metadata and dependencies
├── README.md  # Project documentation
```

## Contributing

We welcome contributions! If you would like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your branch.
4. Open a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with SQLModel and SQLAlchemy for powerful database management.
- Inspired by the need for simple, scalable, and efficient database libraries.

## Contact

For any inquiries or feedback, please contact [your email/contact information].
