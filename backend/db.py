import os
import sqlite3
from datetime import datetime, timezone


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db_path(base_dir: str) -> str:
    return os.path.join(base_dir, "leafcare.db")


def connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          filename TEXT NOT NULL,
          result TEXT NOT NULL,
          description TEXT NOT NULL,
          treatment TEXT NOT NULL,
          confidences_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    con.commit()


def ensure_default_user(con: sqlite3.Connection, email: str, password_hash: str) -> None:
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        return
    cur.execute(
        "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
        (email, password_hash, utc_now_iso()),
    )
    con.commit()

