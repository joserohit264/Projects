import sqlite3
import base64
from typing import Optional, Tuple

DB_PATH = "database/password_manager.db"

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = _get_conn()
    cursor = conn.cursor()

    # users table: username unique, password_hash (base64), salt (base64)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    # passwords table: each row belongs to a user (user_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password BLOB NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# ---------- User management ----------
def register_user(username: str, password_hash_b64: str, salt_b64: str) -> int:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, password_hash_b64, salt_b64)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_user(username: str) -> Optional[Tuple[int, str, str, str]]:
    """
    Returns (id, username, password_hash_b64, salt_b64) or None
    """
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

# ---------- Password entries (per-user) ----------
def add_entry(user_id: int, site: str, username: str, password_blob: bytes, notes: str = ""):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO passwords (user_id, site, username, password, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, site, username, password_blob, notes)
    )
    conn.commit()
    conn.close()

def view_entries(user_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, site, username, password, notes FROM passwords WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_entry(user_id: int, entry_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM passwords WHERE user_id = ? AND id = ?",
        (user_id, entry_id)
    )
    conn.commit()
    conn.close()

def get_entry(user_id: int, entry_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, site, username, password, notes FROM passwords WHERE user_id = ? AND id = ?",
        (user_id, entry_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row
