import re
import requests
import feedparser
from typing import List, Dict, Any
from config import HTTP_PROXY, HTTPS_PROXY
from database import is_news_sent

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

PROXIES = {}
if HTTPS_PROXY or HTTP_PROXY:
    p = HTTPS_PROXY or HTTP_PROXY
    PROXIES = {"http": p, "https": p}

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def get_session(use_proxy: bool = False) -> requests.Session:
    session = requests.Session()
    if use_proxy and PROXIES:
        session.proxies.update(PROXIES)
    else:
        session.trust_env = False
    return session

def fetch_hn_top() -> List[Dict[str, Any]]:
    """Получает самые обсуждаемые мировые IT-новости из Hacker News (score > 100)"""
    url = "https://hn.algolia.com/api/v1/search?tags=front_page&numericFilters=points>100"
    articles = []
    try:
        session = get_session(use_proxy=True)
        resp = session.get(url, headers=HEADERS, timeout=7)
        if resp.status_code == 200:
            hits = resp.json().get("hits", [])
            for h in hits:
                title = h.get("title")
                link = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
                points = h.get("points", 0)
                comments = h.get("num_comments", 0)

                if not title or not link or is_news_sent(link):
                    continue

                summary = f"Популярный пост на Hacker News (Рейтинг: {points} pts, комментариев: {comments}). Первоисточник: {link}"
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": f"Hacker News (Топ • {points} pts)",
                    "category": "🔥 Главное событие в мировом IT"
                })
    except Exception as e:
        print(f"[Curator] Ошибка загрузки Hacker News Top: {e}")
    return articles

def fetch_feed_articles(feed_url: str, source_name: str, category_name: str, use_proxy: bool = False) -> List[Dict[str, Any]]:
    """Парсит указанную RSS-ленту"""
    articles = []
    try:
        session = get_session(use_proxy=use_proxy)
        resp = session.get(feed_url, headers=HEADERS, timeout=7)
        if resp.status_code == 200:
            parsed = feedparser.parse(resp.text)
            for entry in parsed.entries:
                link = getattr(entry, "link", "").strip()
                title = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "")

                if not link or not title or is_news_sent(link):
                    continue

                clean_desc = clean_html(summary)[:1500]
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": clean_desc,
                    "source": source_name,
                    "category": category_name
                })
    except Exception as e:
        print(f"[Curator] Ошибка загрузки {source_name}: {e}")
    return articles

def fetch_curated_digest_candidates() -> Dict[str, List[Dict[str, Any]]]:
    """
    Собирает кандидатов по 4 столпам IT:
    1. fire: Главное мировое событие
    2. ai: ИИ-агенты и технологии
    3. sec: Кибербезопасность
    4. eng: Инженерия и Архитектура
    """
    candidates = {
        "fire": [],
        "ai": [],
        "sec": [],
        "eng": []
    }

    # 1. Главное событие
    candidates["fire"].extend(fetch_hn_top())

    # 2. ИИ-агенты и нейросети
    candidates["ai"].extend(fetch_feed_articles(
        "https://habr.com/ru/rss/hub/artificial_intelligence/top/daily/?fl=ru",
        "Хабр ИИ (Топ)",
        "🤖 ИИ-агенты и технологии",
        use_proxy=False
    ))
    candidates["ai"].extend(fetch_feed_articles(
        "https://simonwillison.net/atom/everything/",
        "Simon Willison AI",
        "🤖 ИИ-агенты и технологии",
        use_proxy=True
    ))

    # 3. Кибербезопасность
    candidates["sec"].extend(fetch_feed_articles(
        "https://feeds.feedburner.com/TheHackersNews",
        "The Hacker News",
        "🛡️ Кибербезопасность",
        use_proxy=True
    ))
    candidates["sec"].extend(fetch_feed_articles(
        "https://habr.com/ru/rss/hub/infosecurity/top/daily/?fl=ru",
        "Хабр ИБ (Топ)",
        "🛡️ Кибербезопасность",
        use_proxy=False
    ))

    # 4. Инженерия и Архитектура
    candidates["eng"].extend(fetch_feed_articles(
        "https://habr.com/ru/rss/articles/top/daily/?fl=ru",
        "Хабр Лучшее (Сутки)",
        "🛠️ Инженерия и Архитектура",
        use_proxy=False
    ))
    candidates["eng"].extend(fetch_feed_articles(
        "https://habr.com/ru/rss/hub/devops/top/daily/?fl=ru",
        "Хабр DevOps (Топ)",
        "🛠️ Инженерия и Архитектура",
        use_proxy=False
    ))

    return candidates
