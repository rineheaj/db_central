# DB Central

DB Central is a Python library designed to simplify database interactions using SQLAlchemy/SQLModel. It provides tools and utilities to streamline data management and accelerate application development.

## Features

- **Flexible ORM Support:** Easily integrate with SQL databases using SQLModel and SQLAlchemy.
- **Simplified Queries:** Utility functions for common database operations.
- **Scalable Design:** Supports a structured approach to building robust applications.
- **Extensibility:** Built to be extended for various use cases.

## Requirements

- Python 3.8 or higher

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/rineheaj/db_central.git
cd db_central
```

Set up your environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Getting Started

### Basic Usage

1. Import the library in your Python project:

   ```python
   from src import db_central
   ```

2. Set up your database connection and start using the library:

   ```python
   from sqlmodel import SQLModel, create_engine

   # Define your database URL
   DATABASE_URL = "sqlite:///example.db"
   engine = create_engine(DATABASE_URL)

   # Initialize your models and tables
   SQLModel.metadata.create_all(engine)
   ```

3. Start performing CRUD operations with ease.

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
