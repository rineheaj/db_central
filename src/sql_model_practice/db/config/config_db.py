from sqlmodel import SQLModel, create_engine

DB_URL = "sqlite:///orm.db"
ENGINE = create_engine(DB_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(ENGINE)

