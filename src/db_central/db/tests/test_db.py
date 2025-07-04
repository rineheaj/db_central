from sqlmodel import select
from db_central.db.models.author_and_book import(
    Author,
    Book,
)


def test_create_author(session):
    author = Author(
        name="Test Author",
        email="test_author_1@gmail.com",
    )
    session.add(author)

    result = session.exec(select(Author).where(Author.name == "Test Author"))
    assert result.first() is not None


def test_create_book(session):
    author = Author(
        name="Test Author",
        email="test_author_1@gmail.com",
    )
    session.add(author)
    session.commit()

    book = Book(
        title="Test Book",
        content="Test Content",
        author_id=author.id,
    )
    session.add(book)
    session.commit()

    result = session.exec(
        select(Book).where(Book.title == "Test Book").where(Book.content == "Test Content")
    )
    assert result.first() is not None

