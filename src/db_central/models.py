"""
Database models for DB Central library.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Author(SQLModel, table=True):
    """
    Author model representing a book author.
    
    Attributes:
        id: Unique identifier for the author
        name: Author's full name (required, max 100 characters)
        email: Author's email address (required, max 100 characters)
        books: List of books written by this author
    """
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="Author's full name")
    email: str = Field(max_length=100, description="Author's email address")

    books: List["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    """
    Book model representing a published book.
    
    Attributes:
        id: Unique identifier for the book
        title: Book title (required, max 200 characters)  
        content: Book content/description (required)
        author_id: Foreign key reference to the author
        author: The author who wrote this book
    """
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, description="Book title")
    content: str = Field(description="Book content or description")
    author_id: int = Field(foreign_key="author.id", description="Author's ID")

    author: Optional[Author] = Relationship(back_populates="books")