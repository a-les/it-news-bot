import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH, BASE_DIR

SENT_FILE = BASE_DIR / "sent_urls.txt"

def init_db():
    if not SENT_FILE.exists():
        SENT_FILE.touch()
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

DEFAULT_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "1057904544"))

def get_active_subscribers():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM subscribers WHERE active = 1")
        rows = cursor.fetchall()
        subs = set([r[0] for r in rows])
        if DEFAULT_CHAT_ID:
            subs.add(DEFAULT_CHAT_ID)
        return list(subs)

def is_news_sent(url: str) -> bool:
    clean_url = url.strip()
    if SENT_FILE.exists():
        try:
            with open(SENT_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if clean_url in content:
                    return True
        except Exception:
            pass

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM sent_news WHERE url = ?", (clean_url,))
        return cursor.fetchone() is not None

def mark_news_sent(url: str, title: str):
    clean_url = url.strip()
    try:
        with open(SENT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{clean_url}\n")
    except Exception:
        pass

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO sent_news (url, title, sent_at)
            VALUES (?, ?, ?)
        """, (clean_url, title.strip(), datetime.now()))
        conn.commit()
