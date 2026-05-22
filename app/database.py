import sqlite3
from datetime import datetime, timezone

DB_PATH = "metadata.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                filename   TEXT    NOT NULL,
                chunk_id   TEXT    NOT NULL,
                chunk_text TEXT    NOT NULL,
                timestamp  TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_chunk(filename: str, chunk_id: str, chunk_text: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chunks (filename, chunk_id, chunk_text, timestamp) VALUES (?, ?, ?, ?)",
            (filename, chunk_id, chunk_text, ts),
        )
        conn.commit()


def delete_all_chunks() -> None:
    """Wipe all chunk records. Called on every new upload (single-doc mode)."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM chunks")
        conn.commit()        


def init_bookings_table() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT    NOT NULL,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL,
                date       TEXT    NOT NULL,
                time       TEXT    NOT NULL,
                timestamp  TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_booking(
    session_id: str, name: str, email: str, date: str, time: str
) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO bookings
               (session_id, name, email, date, time, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, name, email, date, time, ts),
        )
        conn.commit()