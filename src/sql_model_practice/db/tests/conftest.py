import pytest
from sqlmodel import(
    SQLModel,
    Session,
    create_engine,
)
from sql_model_practice.db.models.author_and_book import(
    Author,
    Book,
)

@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="module")
def session(engine):
    with Session(engine) as session:
        yield session


