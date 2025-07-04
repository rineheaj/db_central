# DB Central

DB Central is a Python library designed to simplify database interactions using SQLAlchemy/SQLModel. It provides a high-level API for database operations with built-in error handling, retry mechanisms, and intuitive CRUD operations.

## Features

- **High-Level API:** Simple, intuitive functions for common database operations
- **Error Handling:** Comprehensive error handling with meaningful error messages
- **Retry Mechanisms:** Automatic retry for transient database failures
- **Flexible ORM Support:** Built on SQLModel and SQLAlchemy for powerful database management
- **Type Safety:** Full type hints and validation for better development experience
- **Extensible Design:** Easy to extend for various use cases and custom models

## Requirements

- Python 3.11 or higher
- SQLModel
- SQLAlchemy

## Installation

### From Source

Clone this repository to your local machine:

```bash
git clone https://github.com/rineheaj/db_central.git
cd db_central
```

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

3. **Verify the setup**:
   ```bash
   uv check
   ```

4. **Run the example**:
   ```bash
   uv run python example.py
   ```

### Manual Installation

Install dependencies manually:

```bash
pip install sqlmodel pytest
```

## Getting Started

### Basic Usage

1. Import the library in your Python project:

   ```python
   from db_central import DatabaseManager
   from db_central.db.models.author_and_book import Author, Book
   from db_central.db.operations import author_operations, book_operations
   ```

2. Set up your database connection:

   ```python
   # Initialize the DatabaseManager
   db_manager = DatabaseManager("sqlite:///example.db")
   db_manager.init_database()
   ```

3. Start performing CRUD operations:

   ```python
   # Create an author
   author = author_operations.create_author(
       db_manager, "Jane Doe", "jane@example.com"
   )
   
   # Create a book
   book = book_operations.create_book(
       db_manager, "My Great Novel", "Content here...", author.id
   )
   
   # Read data
   all_authors = author_operations.get_all_authors(db_manager)
   author_books = book_operations.find_books_by_author(db_manager, author.id)
   ```

### DatabaseManager API

The `DatabaseManager` class provides the core functionality:

```python
from db_central import DatabaseManager, DatabaseError

# Initialize with retry configuration
db_manager = DatabaseManager(
    database_url="sqlite:///example.db",
    echo=False,  # Set to True for SQL logging
    max_retries=3,  # Number of retry attempts
    retry_delay=1.0  # Delay between retries in seconds
)

# Initialize database tables
db_manager.init_database()
```

#### Core CRUD Operations

```python
# Create
author = Author(name="John Doe", email="john@example.com")
created_author = db_manager.create(author)

# Read by ID
author = db_manager.read(Author, author_id=1)

# Read all (with optional limit)
all_authors = db_manager.read_all(Author, limit=10)

# Update
author.email = "newemail@example.com"
updated_author = db_manager.update(author)

# Delete
success = db_manager.delete(Author, author_id=1)

# Query with filters
authors = db_manager.query(Author, {"name": "John Doe"})

# Count records
count = db_manager.count(Author)
```

### High-Level Operations

Use the pre-built operation functions for common tasks:

#### Author Operations

```python
from db_central.db.operations import author_operations

# Create author
author = author_operations.create_author(db_manager, "Author Name", "email@example.com")

# Get author by ID
author = author_operations.get_author(db_manager, author_id)

# Get all authors
authors = author_operations.get_all_authors(db_manager, limit=10)

# Find by name
authors = author_operations.find_authors_by_name(db_manager, "John Doe")

# Find by email
authors = author_operations.find_authors_by_email(db_manager, "john@example.com")

# Update author
updated_author = author_operations.update_author(db_manager, author)

# Delete author
success = author_operations.delete_author(db_manager, author_id)
```

#### Book Operations

```python
from db_central.db.operations import book_operations

# Create book
book = book_operations.create_book(db_manager, "Title", "Content", author_id)

# Get book by ID
book = book_operations.get_book(db_manager, book_id)

# Get all books
books = book_operations.get_all_books(db_manager, limit=10)

# Find by title
books = book_operations.find_books_by_title(db_manager, "Book Title")

# Find by author
books = book_operations.find_books_by_author(db_manager, author_id)

# Update book
updated_book = book_operations.update_book(db_manager, book)

# Delete book
success = book_operations.delete_book(db_manager, book_id)
```

### Error Handling

DB Central provides comprehensive error handling:

```python
from db_central import DatabaseError, ConnectionError, ValidationError

try:
    # Database operations
    author = db_manager.create(author)
except ConnectionError as e:
    print(f"Database connection failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
except DatabaseError as e:
    print(f"Database operation failed: {e}")
```

### Custom Models

Define your own models using SQLModel:

```python
from sqlmodel import SQLModel, Field

class MyModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str

# Use with DatabaseManager
db_manager.create(MyModel(name="Example", description="Example description"))
```

## Examples

### Complete Example

```python
from db_central import DatabaseManager
from db_central.db.models.author_and_book import Author, Book
from db_central.db.operations import author_operations, book_operations

def main():
    # Initialize database
    db_manager = DatabaseManager("sqlite:///bookstore.db")
    db_manager.init_database()
    
    # Create an author
    author = author_operations.create_author(
        db_manager, "J.K. Rowling", "jk@example.com"
    )
    
    # Create books
    book1 = book_operations.create_book(
        db_manager, "Harry Potter", "A young wizard...", author.id
    )
    
    # Query data
    all_books = book_operations.find_books_by_author(db_manager, author.id)
    print(f"Found {len(all_books)} books by {author.name}")

if __name__ == "__main__":
    main()
```

See `example.py` for a comprehensive demonstration of all features.

## Testing

Run the test suite:

```bash
# Run original tests
PYTHONPATH=src python -m pytest src/db_central/db/tests/test_db.py -v

# Run new DatabaseManager tests (in separate environment)
PYTHONPATH=src python -m pytest test_new/test_database_manager.py -v
```

## Repository Structure

```
db_central/
├── src/
│   └── db_central/          # Main library code
│       ├── database_manager.py     # Core DatabaseManager class
│       ├── db/
│       │   ├── config/
│       │   │   └── config_db.py    # Database configuration
│       │   ├── models/
│       │   │   └── author_and_book.py  # Sample models
│       │   ├── operations/
│       │   │   ├── author_operations.py  # Author CRUD operations
│       │   │   └── book_operations.py    # Book CRUD operations
│       │   └── tests/               # Test files
│       └── __init__.py              # Package exports
├── example.py               # Comprehensive usage example
├── test_new/               # Additional test files
├── pyproject.toml          # Project configuration
├── README.md               # This file
└── .gitignore             # Git ignore patterns
```

## API Reference

### DatabaseManager

- `__init__(database_url, echo=False, max_retries=3, retry_delay=1.0)`
- `init_database()` - Initialize database tables
- `create(model_instance)` - Create a new record
- `read(model_class, model_id)` - Read a record by ID
- `read_all(model_class, limit=None)` - Read all records
- `update(model_instance)` - Update a record
- `delete(model_class, model_id)` - Delete a record
- `query(model_class, filters)` - Query with filters
- `count(model_class)` - Count records

### Exception Classes

- `DatabaseError` - Base exception for database operations
- `ConnectionError` - Database connection failures
- `ValidationError` - Input validation errors

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes with appropriate tests
4. Ensure all tests pass
5. Submit a pull request

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with SQLModel and SQLAlchemy for powerful database management
- Inspired by the need for simple, scalable, and efficient database libraries
- Thanks to the open-source community for the excellent tools and libraries

## Contact

For any inquiries or feedback, please contact [joshtrineheart@gmail.com] or open an issue on GitHub.