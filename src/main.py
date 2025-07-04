from db_central.db.config.config_db import (
    init_db,
)


def main():
    init_db()
    print("DATABASE STARTED")


if __name__ == "__main__":
    main()
