# DB Central

DB Central is a Python library designed to simplify database interactions using SQLAlchemy/SQLModel. It provides tools and utilities to streamline data management and accelerate application development with clean, intuitive APIs for database operations.

## Features

- **High-Level API:** Simple CRUD operations with intuitive method names
- **Flexible ORM Support:** Built on SQLModel and SQLAlchemy for powerful database management
- **Error Handling:** Comprehensive error handling with meaningful error messages
- **Connection Management:** Robust connection management with retry mechanisms
- **Type Safety:** Full type hints for better development experience
- **Validation:** Built-in validation for data integrity
- **Extensibility:** Built to be extended for various use cases

## Requirements

- Python 3.11 or higher
- SQLModel
- SQLAlchemy

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/rineheaj/db_central.git
cd db_central
```

Set up your environment and install dependencies:

```bash
pip install sqlmodel pytest
```

## Quick Start

### Basic Usage

```python
from db_central import DatabaseManager, Author, Book

# Initialize the database manager
db = DatabaseManager("sqlite:///my_app.db")
db.initialize_tables()

# Create records
author = db.create(Author(name="Jane Doe", email="jane@example.com"))
book = db.create(Book(
    title="My Book", 
    content="Great content here...", 
    author_id=author.id
))

# Read records
all_authors = db.get_all(Author)
author_by_id = db.get_by_id(Author, author.id)
books_by_author = db.find_by(Book, author_id=author.id)

# Update records
author.email = "jane.doe@example.com"
updated_author = db.update(author)

# Delete records
deleted = db.delete(Book, book.id)
```

### Advanced Usage

```python
# Custom database configuration
db = DatabaseManager(
    database_url="postgresql://user:pass@localhost/mydb",
    echo=True  # Enable SQL logging
)

# Error handling
from db_central import DatabaseError, ValidationError

try:
    author = db.create(Author(name="", email="invalid"))
except ValidationError as e:
    print(f"Validation failed: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")

# Session management for complex operations
with db.session() as session:
    author = Author(name="Complex Author", email="complex@example.com")
    session.add(author)
    # Session automatically commits on success or rolls back on error
```

## API Reference

### DatabaseManager

The main class for database interactions.

#### Constructor

```python
DatabaseManager(database_url: str = "sqlite:///orm.db", echo: bool = False)
```

- `database_url`: Database connection URL (defaults to SQLite)
- `echo`: Enable SQL query logging

#### Core Methods

**`initialize_tables() -> None`**
Creates all tables defined in the models.

**`create(obj: SQLModel) -> SQLModel`**
Create a new record in the database.

**`get_by_id(model_class: Type[SQLModel], obj_id: int) -> Optional[SQLModel]`**
Retrieve a record by its ID.

**`get_all(model_class: Type[SQLModel], limit: Optional[int] = None) -> List[SQLModel]`**
Retrieve all records of a given model type.

**`update(obj: SQLModel) -> SQLModel`**
Update an existing record in the database.

**`delete(model_class: Type[SQLModel], obj_id: int) -> bool`**
Delete a record by its ID.

**`find_by(model_class: Type[SQLModel], **kwargs) -> List[SQLModel]`**
Find records by specific field values.

### Models

#### Author

```python
class Author(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    books: List["Book"] = Relationship(back_populates="author")
```

#### Book

```python
class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    content: str
    author_id: int = Field(foreign_key="author.id")
    author: Optional[Author] = Relationship(back_populates="books")
```

### Exception Classes

- **`DatabaseError`**: Base exception for database operations
- **`ConnectionError`**: Exception raised when database connection fails
- **`ValidationError`**: Exception raised when data validation fails

## Examples

See the `examples/` directory for complete usage examples:

- `examples/basic_usage.py`: Comprehensive example showing all CRUD operations
- Run with: `python examples/basic_usage.py`

## Running Tests

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest src/db_central/tests/test_database_manager.py -v
```

## Repository Structure

```
db_central/
├── src/
│   └── db_central/           # Main library code
│       ├── __init__.py       # DatabaseManager and main API
│       ├── db/               # Database configuration and models
│       │   ├── config/       # Database configuration
│       │   ├── models/       # SQLModel definitions
│       │   ├── tests/        # Legacy tests (still supported)
│       │   └── seeds/        # Database seeding utilities
│       └── tests/            # New API tests
├── examples/                 # Usage examples
├── orm.db                    # Example SQLite database file
├── .gitignore               # Ignored files for Git
├── .python-version          # Python version used
├── pyproject.toml           # Project metadata and dependencies
└── README.md                # Project documentation
```

## Migration from sql_model_practice

If you're migrating from the old `sql_model_practice` package:

1. Update imports:
   ```python
   # Old
   from sql_model_practice.db.models.author_and_book import Author, Book
   
   # New
   from db_central import DatabaseManager, Author, Book
   ```

2. Use the new high-level API:
   ```python
   # Old - manual session management
   with Session(engine) as session:
       author = Author(name="Test", email="test@example.com")
       session.add(author)
       session.commit()
   
   # New - simplified API
   db = DatabaseManager()
   author = db.create(Author(name="Test", email="test@example.com"))
   ```

## Contributing

We welcome contributions! If you would like to contribute:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Write tests for your changes
4. Ensure all tests pass
5. Commit your changes and push to your branch
6. Open a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/rineheaj/db_central.git
cd db_central

# Install dependencies
pip install sqlmodel pytest

# Run tests
python -m pytest

# Run examples
python examples/basic_usage.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with SQLModel and SQLAlchemy for powerful database management
- Inspired by the need for simple, scalable, and efficient database libraries

## Contact

For any inquiries or feedback, please contact [your email/contact information].

---

**Version**: 0.1.0  
**Python**: 3.11+  
**License**: MIT
