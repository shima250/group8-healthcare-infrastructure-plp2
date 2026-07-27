"""
Schema
------
users
    id                INTEGER PRIMARY KEY
    name              TEXT
    avg_cycle_length  INTEGER

cycle_history
    id          INTEGER PRIMARY KEY
    user_id     INTEGER   -- FK -> users.id
    start_date  TEXT      -- "YYYY-MM-DD"
"""

import sqlite3
from pathlib import Path


class Database:
    """Wraps a single SQLite connection and all raw SQL for SafeCycle."""

    def __init__(self, db_path="safecycle.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                avg_cycle_length INTEGER NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cycle_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    # -- generic helpers --------------------------------------------------

    def execute(self, query, params=()):
        """Run an INSERT/UPDATE/DELETE. Returns (lastrowid, rowcount)."""
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur.lastrowid, cur.rowcount

    def fetch_one(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        self.conn.close()

    # -- domain-specific methods -------------------------------------------
    # (Kept here, not in User/CycleTracker, so those classes never touch SQL)
    def get_all_users(self):
    """Return all users from the database."""
        return self.fetch_all("SELECT * FROM users ORDER BY id ASC")


    
    def insert_user(self, name, avg_cycle_length):
        new_id, _ = self.execute(
            "INSERT INTO users (name, avg_cycle_length) VALUES (?, ?)",
            (name, avg_cycle_length),
        )
        return new_id

    def get_user_row(self, user_id):
        return self.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    def update_user_row(self, user_id, avg_cycle_length):
        _, rowcount = self.execute(
            "UPDATE users SET avg_cycle_length = ? WHERE id = ?",
            (avg_cycle_length, user_id),
        )
        return rowcount > 0

    def insert_period(self, user_id, start_date):
        new_id, _ = self.execute(
            "INSERT INTO cycle_history (user_id, start_date) VALUES (?, ?)",
            (user_id, start_date),
        )
        return new_id

    def get_history_rows(self, user_id):
        return self.fetch_all(
            "SELECT * FROM cycle_history WHERE user_id = ? ORDER BY start_date ASC",
            (user_id,),
        )

    def get_latest_period_row(self, user_id):
        return self.fetch_one(
            "SELECT * FROM cycle_history WHERE user_id = ? ORDER BY start_date DESC LIMIT 1",
            (user_id,),
        )

    def update_period_row(self, entry_id, new_start_date):
        _, rowcount = self.execute(
            "UPDATE cycle_history SET start_date = ? WHERE id = ?",
            (new_start_date, entry_id),
        )
        return rowcount > 0

    def delete_period_row(self, entry_id):
        _, rowcount = self.execute(
            "DELETE FROM cycle_history WHERE id = ?", (entry_id,)
        )
        return rowcount > 0
