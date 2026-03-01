import sqlite3
from collections.abc import Generator
from typing import Annotated

from fastapi.params import Depends

from config import DB_PATH
from contextlib import contextmanager


@contextmanager
def get_db():
    """Yield a DB connection with row_factory returning dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _row_factory
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create messages table if it does not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages (message TEXT, created_at TEXT)"
        )
        conn.commit()


def _row_factory(cursor, row):
    return {cursor.description[i][0]: row[i] for i in range(len(row))}


def get_db_dependency() -> Generator[sqlite3.Connection]:
    with get_db() as conn:
        yield conn


GetDB = Annotated[
    sqlite3.Connection,
    Depends(get_db_dependency),
]


def main():
    init_db()
    with get_db() as conn:
        conn.executemany(
            "INSERT INTO messages (message, created_at) VALUES (?, datetime('now'))",
            [
                ("Welcome to the guestbook!",),
                ("Leave a message in this guestbook.",),
                ("Try the word guestbook in your message.",),
            ],
        )
        conn.commit()
    print("DB initialized with sample messages.")


if __name__ == "__main__":
    main()
