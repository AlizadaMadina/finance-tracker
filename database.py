"""
database.py — SQLite setup and schema for Finance Tracker
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/finance.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL DEFAULT 'Uncategorized',
            account     TEXT,
            notes       TEXT,
            imported_at TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL UNIQUE,
            monthly_limit REAL  NOT NULL
        );

        CREATE TABLE IF NOT EXISTS category_rules (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword     TEXT    NOT NULL,
            category    TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized at", DB_PATH)


if __name__ == "__main__":
    init_db()
