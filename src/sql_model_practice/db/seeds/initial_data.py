# src/my_packaged_app/db/seeds/initial_data.py
from sqlmodel import Session, select
from sql_model_practice.db.config.config_db import ENGINE
from sql_model_practice.db.models.author_and_book import(
    Author,
    Book,
)



def create_initial_data():
    with Session(ENGINE) as session:
        #---Create authors---
        author1 = Author(name="Dr. Sillypants", email="SillyPants@gmail.com")
        author2 = Author(name="Captain Quirk", email="CaptainQ@gmail.com")
        author3 = Author(name="Professor Wobble", email="ProWob@gmail.com")


        #---Create books---
        book1 = Book(title="The Adventures of Sillypants", content="A tale of wacky adventures and nonsensical escapades.", author=author1)
        book2 = Book(title="Quirk's Quirky Quests", content="Join Captain Quirk on his bizarre and whimsical journeys.", author=author2)
        book3 = Book(title="Wobble's Wacky World", content="Explore the eccentric world of Professor Wobble.", author=author3)
        book4 = Book(title="Sillypants Strikes Again", content="More absurd adventures with Dr. Sillypants.", author=author1)
        book5 = Book(title="Quirk's Quirky Quests: The Sequel", content="Captain Quirk's even quirkier quests continue.", author=author2)
        book6 = Book(title="Wobble's Wacky World: Part Two", content="Professor Wobble's world gets even wackier.", author=author3)

        #---Add books to the session---

        session.add_all(
            [
                author1, author2, author3,
                book1, book2, book3, book4, book5, book6, 
            ]
        )

        session.commit()

def test_conn():
    with Session(ENGINE) as session:
        result = session.exec(
            select(Author).where(Author.name == "Professor Wobble")
        )
        author = result.first()
        if not author:
            print("NO AUTHOR FOUND IN DV")
        else:
            print(author.name)


if __name__ == "__main__":
    create_initial_data()
    test_conn()
