import random
import sqlite3
from datetime import date, datetime, timedelta

from config import DB_PATH


def register_adapters_and_converters():
    sqlite3.register_adapter(
        date,
        lambda d: d.isoformat(),
    )
    sqlite3.register_adapter(
        datetime,
        lambda dt: dt.isoformat(),
    )
    sqlite3.register_converter(
        "date",
        lambda b: date.fromisoformat(b.decode()),
    )
    sqlite3.register_converter(
        "datetime",
        lambda b: datetime.fromisoformat(b.decode()),
    )
    sqlite3.register_converter(
        "timestamp",
        lambda b: datetime.fromisoformat(b.decode()),
    )


def get_conn() -> sqlite3.Connection:
    register_adapters_and_converters()
    conn = sqlite3.connect(
        DB_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    conn.row_factory = sqlite3.Row

    return conn


def insert_sample_articles(conn: sqlite3.Connection):
    # Insert sample articles
    sample_articles = [
        ("Web Development Article", "Article about Web Development"),
        ("Python Tutorial", "Learn Python programming"),
        (
            "Introduction to Python Backend Development",
            "Start your first Python Backend",
        ),
        ("Security Basics", "Introduction to web security"),
        ("SQL Injection Demo", "This is a vulnerable application"),
    ]
    start_date = datetime.now() - timedelta(days=len(sample_articles) * 30)
    for idx, (title, content) in enumerate(sample_articles):
        created_at = (
            start_date
            + timedelta(days=idx * random.randint(1, 30))
            + timedelta(minutes=random.random() * 10 * idx)
        ).replace(microsecond=0)
        conn.execute(
            "INSERT INTO articles (title, content, created_at) VALUES (?, ?, ?)",
            (
                title,
                content,
                created_at,
            ),
        )
    conn.commit()
    print("Database initialized with sample data")


def init_db():
    conn = get_conn()

    # Create table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if we already have data
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    if count == 0:
        insert_sample_articles(conn)

    conn.close()


if __name__ == "__main__":
    init_db()
