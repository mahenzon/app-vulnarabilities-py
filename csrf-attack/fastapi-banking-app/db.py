"""
Database initialization script for FastAPI CSRF example.

This script creates the SQLite database with tables and sample data.
Run this script before starting the FastAPI application.
"""

import sys
import sqlite3

from config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables and sample data"""
    print(f"Initializing database at: {DB_PATH}")

    conn = get_db()
    cursor = conn.cursor()

    # Create tables
    print("Creating tables...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 1000.0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (from_user_id) REFERENCES user (id),
            FOREIGN KEY (to_user_id) REFERENCES user (id)
        )
    """)

    # Insert sample users if they don't exist
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]

    if user_count == 0:
        print("Inserting sample users...")
        cursor.execute(
            "INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
            ("alice", "alice123", 1000.0),
        )
        cursor.execute(
            "INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
            ("bob", "bob123", 500.0),
        )
        cursor.execute(
            "INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
            ("attacker", "attacker123", 100.0),
        )
        print("Sample users created:")
        print("  - alice / alice123 (Balance: $1000)")
        print("  - bob / bob123 (Balance: $500)")
        print("  - attacker / attacker123 (Balance: $100)")
    else:
        print(
            f"Database already contains {user_count} users. Skipping sample data insertion."
        )

    conn.commit()
    conn.close()

    print("Database initialization complete!")


def reset_db():
    """Reset the database by deleting and recreating it"""
    if DB_PATH.exists():
        print(f"Deleting existing database: {DB_PATH}")
        DB_PATH.unlink()
    init_db()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("Resetting database...")
        reset_db()
    else:
        init_db()
