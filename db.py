"""
SafeCycle Database Layer
MySQL (Aiven) primary with SQLite fallback.
All raw SQL is confined to this file — other modules call these functions only.
"""

import os
import sqlite3
from datetime import datetime

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# --- Connection Config ---
MYSQL_CONFIG = {
    "host": os.environ.get("SC_MYSQL_HOST", "mysql-27d8e0c3-alustudent-2929.k.aivencloud.com"),
    "port": int(os.environ.get("SC_MYSQL_PORT", 26050)),
    "user": os.environ.get("SC_MYSQL_USER", "avnadmin"),
    "password": os.environ.get("SC_MYSQL_PASSWORD", ""),
    "database": os.environ.get("SC_MYSQL_DB", "safecycle_db"),
}

SQLITE_PATH = os.environ.get("SC_SQLITE_PATH", "safecycle.db")

# Module-level state
_connection = None
_db_type = None  # "mysql" or "sqlite"


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _connect_mysql():
    """Attempt to open a persistent MySQL connection."""
    if not MYSQL_AVAILABLE:
        return None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        conn.autocommit = True
        return conn
    except Exception:
        return None


def _connect_sqlite():
    """Open a persistent SQLite connection."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _connection_alive():
    """Check if the current connection is still usable."""
    if _connection is None:
        return False
    if _db_type == "mysql":
        try:
            return _connection.is_connected()
        except Exception:
            return False
    return True


def get_connection():
    """Return the active database connection, creating one if needed."""
    global _connection, _db_type
    if _connection_alive():
        return _connection
    # Try MySQL first
    _connection = _connect_mysql()
    if _connection:
        _db_type = "mysql"
        return _connection
    # Fallback to SQLite
    _connection = _connect_sqlite()
    _db_type = "sqlite"
    return _connection


def get_db_type():
    """Return 'mysql' or 'sqlite'."""
    get_connection()
    return _db_type


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------

MYSQL_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    avg_cycle_length INT DEFAULT 28
);

CREATE TABLE IF NOT EXISTS cycle_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    start_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

SQLITE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    avg_cycle_length INTEGER DEFAULT 28
);

CREATE TABLE IF NOT EXISTS cycle_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    if _db_type == "mysql":
        for stmt in MYSQL_TABLES.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
    else:
        conn.execute("PRAGMA foreign_keys = ON")
        for stmt in SQLITE_TABLES.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
    cur.close()


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(name, avg_cycle_length=28):
    """Insert a new user. Returns the new user id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, avg_cycle_length) VALUES (%s, %s)"
        if _db_type == "mysql"
        else "INSERT INTO users (name, avg_cycle_length) VALUES (?, ?)",
        (name, avg_cycle_length),
    )
    uid = cur.lastrowid
    cur.close()
    return uid


def get_user(user_id):
    """Fetch a user row as a dict, or None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, avg_cycle_length FROM users WHERE id = %s"
        if _db_type == "mysql"
        else "SELECT id, name, avg_cycle_length FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    if _db_type == "mysql":
        return {"id": row[0], "name": row[1], "avg_cycle_length": row[2]}
    return dict(row)


def update_user_cycle_length(user_id, new_length):
    """Update a user's average cycle length."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET avg_cycle_length = %s WHERE id = %s"
        if _db_type == "mysql"
        else "UPDATE users SET avg_cycle_length = ? WHERE id = ?",
        (new_length, user_id),
    )
    cur.close()


# ---------------------------------------------------------------------------
# Cycle history CRUD
# ---------------------------------------------------------------------------

def add_period_entry(user_id, start_date):
    """Log a period start date (str 'YYYY-MM-DD'). Returns the new entry id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cycle_history (user_id, start_date) VALUES (%s, %s)"
        if _db_type == "mysql"
        else "INSERT INTO cycle_history (user_id, start_date) VALUES (?, ?)",
        (user_id, start_date),
    )
    eid = cur.lastrowid
    cur.close()
    return eid


def get_history(user_id):
    """Return all period entries for a user, ordered newest first."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, start_date FROM cycle_history WHERE user_id = %s ORDER BY start_date DESC"
        if _db_type == "mysql"
        else "SELECT id, user_id, start_date FROM cycle_history WHERE user_id = ? ORDER BY start_date DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    result = []
    for row in rows:
        if _db_type == "mysql":
            result.append({"id": row[0], "user_id": row[1], "start_date": str(row[2])})
        else:
            result.append(dict(row))
    return result


def get_latest_entry(user_id):
    """Return the most recent period entry for a user, or None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, start_date FROM cycle_history WHERE user_id = %s ORDER BY start_date DESC LIMIT 1"
        if _db_type == "mysql"
        else "SELECT id, user_id, start_date FROM cycle_history WHERE user_id = ? ORDER BY start_date DESC LIMIT 1",
        (user_id,),
    )
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    if _db_type == "mysql":
        return {"id": row[0], "user_id": row[1], "start_date": str(row[2])}
    return dict(row)


def update_period_entry(entry_id, new_date):
    """Update the start_date of a specific period entry."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cycle_history SET start_date = %s WHERE id = %s"
        if _db_type == "mysql"
        else "UPDATE cycle_history SET start_date = ? WHERE id = ?",
        (new_date, entry_id),
    )
    cur.close()


def delete_period_entry(entry_id):
    """Delete a specific period entry."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cycle_history WHERE id = %s"
        if _db_type == "mysql"
        else "DELETE FROM cycle_history WHERE id = ?",
        (entry_id,),
    )
    cur.close()


# ---------------------------------------------------------------------------
# Self-test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== SafeCycle db.py Self-Test ===\n")
    init_db()
    print(f"Connected via: {get_db_type().upper()}")
    print(f"Tables created.\n")

    # Create a test user
    uid = create_user("Test User", 30)
    print(f"Created user id={uid}")
    user = get_user(uid)
    print(f"Retrieved user: {user}")

    # Update cycle length
    update_user_cycle_length(uid, 27)
    user = get_user(uid)
    print(f"After update: {user}\n")

    # Add period entries
    e1 = add_period_entry(uid, "2026-06-01")
    e2 = add_period_entry(uid, "2026-06-29")
    e3 = add_period_entry(uid, "2026-07-26")
    print(f"Added entries: {e1}, {e2}, {e3}")

    # Read history
    history = get_history(uid)
    print(f"History (newest first): {history}")

    # Latest entry
    latest = get_latest_entry(uid)
    print(f"Latest entry: {latest}")

    # Update an entry
    update_period_entry(e2, "2026-06-30")
    updated = [e for e in get_history(uid) if e["id"] == e2]
    print(f"After update entry {e2}: {updated}")

    # Delete an entry
    delete_period_entry(e3)
    history_after = get_history(uid)
    print(f"After deleting {e3}: {history_after}")

    print("\n=== All tests passed! ===")
