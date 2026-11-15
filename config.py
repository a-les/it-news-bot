import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Telegram & AI tokens
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Proxy
HTTP_PROXY = os.getenv("HTTP_PROXY", "").strip()
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "").strip()

# Digest settings (UTC+6)
MORNING_HOUR = int(os.getenv("MORNING_HOUR", "7"))
EVENING_HOUR = int(os.getenv("EVENING_HOUR", "19"))
NEWS_PER_DIGEST = int(os.getenv("NEWS_PER_DIGEST", "5"))

# RSS Feeds to monitor
RSS_FEEDS = [
    {
        "name": "Хабр ИИ",
        "url": "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru",
        "category": "Искусственный интеллект и LLM"
    },
    {
        "name": "Хабр ИБ",
        "url": "https://habr.com/ru/rss/hub/infosecurity/all/?fl=ru",
        "category": "Кибербезопасность"
    },
    {
        "name": "Хабр Разработка",
        "url": "https://habr.com/ru/rss/hub/programming/all/?fl=ru",
        "category": "Разработка и Архитектура"
    },
    {
        "name": "Хабр DevOps и Инфраструктура",
        "url": "https://habr.com/ru/rss/hub/devops/all/?fl=ru",
        "category": "DevOps, Облака и Агенты"
    },
    {
        "name": "Хабр IT-Инфраструктура",
        "url": "https://habr.com/ru/rss/hub/it-infrastructure/all/?fl=ru",
        "category": "Системный дизайн и Базы данных"
    },
    {
        "name": "The Hacker News",
        "url": "https://thehackernews.com/feeds/posts/default",
        "category": "Кибербезопасность (Мировые новости)"
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "category": "Кибербезопасность и Уязвимости"
    },
    {
        "name": "Simon Willison AI",
        "url": "https://simonwillison.net/atom/everything/",
        "category": "Практический AI, LLM и Агенты"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "Искусственный интеллект (Тренды)"
    }
]

# Database path
DB_PATH = BASE_DIR / "news_bot.db"
