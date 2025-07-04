# DB Central

**A Python SQL Wrapper Library That Simplifies Database Interactions**

DB Central is designed to make database operations accessible to developers who are unfamiliar with SQL models. It provides an intuitive, high-level API that abstracts SQL complexities while maintaining the power and flexibility of SQLAlchemy and SQLModel under the hood.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🚀 Simple API**: Intuitive methods for Create, Read, Update, and Delete (CRUD) operations
- **🛡️ Robust Error Handling**: Comprehensive error management for connection failures, validation errors, and query issues
- **🔍 Smart Validation**: Built-in input validation with meaningful error messages
- **🔗 Relationship Support**: Easy handling of database relationships and foreign keys
- **🔎 Search Functionality**: Built-in search capabilities across your data
- **📊 Statistics & Reporting**: Get insights about your database with built-in statistics
- **🔧 Flexible Configuration**: Support for multiple database backends via SQLAlchemy
- **📝 Comprehensive Documentation**: Extensive docstrings and examples
- **🧪 Well Tested**: Comprehensive test suite ensuring reliability

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rineheaj/db_central.git
   cd db_central
   ```

2. **Install dependencies**:
   ```bash
   pip install sqlmodel pytest
   ```

3. **Run the example**:
   ```bash
   python examples/basic_usage.py
   ```

### Basic Usage

```python
from db_central import create_database_manager

# Create a database manager (defaults to SQLite)
db = create_database_manager("sqlite:///my_app.db")

# Create an author
author = db.create_author("Jane Doe", "jane@example.com")
print(f"Created author: {author.name} (ID: {author.id})")

# Create a book
book = db.create_book(
    title="Python for Beginners", 
    content="A comprehensive guide to Python programming",
    author_id=author.id
)
print(f"Created book: {book.title}")

# Read operations
all_authors = db.get_all_authors()
author_books = db.get_books_by_author(author.id)

# Search functionality
python_books = db.search_books("Python")

# Update operations
updated_author = db.update_author(author.id, name="Jane Smith")
updated_book = db.update_book(book.id, title="Advanced Python Programming")

# Database statistics
stats = db.get_database_stats()
print(f"Database has {stats['authors']} authors and {stats['books']} books")

# Always close the connection when done
db.close()
```

### Using Context Manager (Recommended)

```python
from db_central import create_database_manager

# Context manager automatically handles connection cleanup
with create_database_manager("sqlite:///my_app.db") as db:
    # Create and work with your data
    author = db.create_author("John Smith", "john@example.com")
    book = db.create_book("My Book", "Book content", author.id)
    
    # Database connection automatically closed when exiting the block
```

## 📖 API Reference

### DatabaseManager

The main class for all database operations.

#### Author Operations

- **`create_author(name: str, email: str) -> Author`**: Create a new author
- **`get_author(author_id: int) -> Author`**: Get an author by ID
- **`get_all_authors() -> List[Author]`**: Get all authors
- **`update_author(author_id: int, name: str = None, email: str = None) -> Author`**: Update author information
- **`delete_author(author_id: int) -> bool`**: Delete an author and all their books

#### Book Operations

- **`create_book(title: str, content: str, author_id: int) -> Book`**: Create a new book
- **`get_book(book_id: int) -> Book`**: Get a book by ID
- **`get_all_books() -> List[Book]`**: Get all books
- **`get_books_by_author(author_id: int) -> List[Book]`**: Get all books by a specific author
- **`update_book(book_id: int, title: str = None, content: str = None, author_id: int = None) -> Book`**: Update book information
- **`delete_book(book_id: int) -> bool`**: Delete a book

#### Utility Operations

- **`search_books(query: str) -> List[Book]`**: Search books by title or content
- **`get_database_stats() -> Dict[str, int]`**: Get database statistics
- **`close()`**: Close database connection

### Models

#### Author
- **`id`**: Unique identifier (auto-generated)
- **`name`**: Author's full name (max 100 characters)
- **`email`**: Author's email address (max 100 characters, must be unique)
- **`books`**: List of books written by this author

#### Book
- **`id`**: Unique identifier (auto-generated)
- **`title`**: Book title (max 200 characters)
- **`content`**: Book content or description
- **`author_id`**: Reference to the author
- **`author`**: The author who wrote this book

## 🛡️ Error Handling

DB Central provides comprehensive error handling with meaningful error messages:

```python
from db_central import create_database_manager
from db_central.exceptions import ValidationError, NotFoundError

try:
    db = create_database_manager()
    
    # This will raise a ValidationError
    author = db.create_author("", "invalid-email")
    
except ValidationError as e:
    print(f"Validation error: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Exception Types

- **`DBCentralError`**: Base exception for all DB Central errors
- **`ConnectionError`**: Database connection failures
- **`ValidationError`**: Input validation failures
- **`NotFoundError`**: Requested records not found
- **`QueryError`**: SQL query execution failures

## 📁 Project Structure

```
db_central/
├── src/
│   └── db_central/
│       ├── __init__.py          # Main library exports
│       ├── database_manager.py  # Core DatabaseManager class
│       ├── models.py           # Database models (Author, Book)
│       └── exceptions.py       # Custom exceptions
├── examples/
│   ├── basic_usage.py          # Basic usage example
│   ├── error_handling.py       # Error handling examples
│   └── advanced_usage.py       # Advanced features demo
├── tests/
│   ├── conftest.py             # Test configuration
│   ├── test_author_operations.py
│   ├── test_book_operations.py
│   └── test_database_manager.py
├── README.md                   # This file
└── pyproject.toml             # Project configuration
```

## 🔧 Configuration

### Database URLs

DB Central supports any database supported by SQLAlchemy:

```python
# SQLite (default)
db = create_database_manager("sqlite:///my_database.db")

# PostgreSQL
db = create_database_manager("postgresql://user:password@localhost/dbname")

# MySQL
db = create_database_manager("mysql://user:password@localhost/dbname")

# In-memory SQLite (for testing)
db = create_database_manager("sqlite:///:memory:")
```

### Debugging

Enable SQL query logging for debugging:

```python
db = create_database_manager("sqlite:///my_db.db", echo=True)
```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=db_central --cov-report=html

# Run specific test file
python -m pytest tests/test_author_operations.py -v
```

## 📚 Examples

The `examples/` directory contains comprehensive examples:

- **`basic_usage.py`**: Introduction to core functionality
- **`error_handling.py`**: Demonstrates error handling patterns
- **`advanced_usage.py`**: Advanced features like bulk operations and statistics

Run any example:
```bash
python examples/basic_usage.py
python examples/error_handling.py
python examples/advanced_usage.py
```

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `python -m pytest tests/`
5. Commit your changes: `git commit -m "Add my feature"`
6. Push to your branch: `git push origin feature/my-feature`
7. Open a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/rineheaj/db_central.git
cd db_central

# Install dependencies
pip install sqlmodel pytest

# Run tests to ensure everything works
python -m pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [SQLModel](https://sqlmodel.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/) for powerful database management
- Inspired by the need for simple, scalable, and efficient database libraries
- Thanks to the Python community for creating amazing tools

## 📞 Support

For questions, issues, or feature requests:

- **GitHub Issues**: [https://github.com/rineheaj/db_central/issues](https://github.com/rineheaj/db_central/issues)
- **Email**: joshtrineheart@gmail.com

---

**DB Central** - Making database interactions simple and intuitive for everyone! 🚀
