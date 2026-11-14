import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                sent_at TIMESTAMP
            )
        """)
        conn.commit()

def add_subscriber(chat_id: int, username: str = "", first_name: str = ""):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscribers (chat_id, username, first_name, joined_at, active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(chat_id) DO UPDATE SET active = 1, username = excluded.username, first_name = excluded.first_name
        """, (chat_id, username or "", first_name or "", datetime.now()))
        conn.commit()

def set_subscriber_status(chat_id: int, active: bool):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET active = ? WHERE chat_id = ?", (1 if active else 0, chat_id))
        conn.commit()

def get_active_subscribers():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM subscribers WHERE active = 1")
        rows = cursor.fetchall()
        return [r[0] for r in rows]

def is_news_sent(url: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM sent_news WHERE url = ?", (url.strip(),))
        return cursor.fetchone() is not None

def mark_news_sent(url: str, title: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO sent_news (url, title, sent_at)
            VALUES (?, ?, ?)
        """, (url.strip(), title.strip(), datetime.now()))
        conn.commit()
