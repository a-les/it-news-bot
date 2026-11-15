import os
import sys
import time
import requests
from config import TELEGRAM_BOT_TOKEN
from database import init_db, mark_news_sent
from rss_fetcher import fetch_curated_digest_candidates
from ai_mentor import AIMentor

# Чат пользователя (по умолчанию ваш ID, или из переменной окружения)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1057904544")

def send_telegram_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200 and r.json().get("ok", False)
    except Exception as e:
        print(f"[Send] Ошибка отправки в Telegram: {e}")
        return False

def run_digest():
    init_db()
    mentor = AIMentor()

    print("[Digest] Сбор кандидатов по 4 столпам IT...")
    candidates = fetch_curated_digest_candidates()

    pillars = [
        ("fire", "🔥 Главное событие в мировом IT"),
        ("ai", "🤖 ИИ-агенты и технологии"),
        ("sec", "🛡️ Кибербезопасность"),
        ("eng", "🛠️ Инженерия и Архитектура")
    ]

    sent_count = 0

    for pillar_key, pillar_label in pillars:
        articles = candidates.get(pillar_key, [])
        for art in articles:
            print(f"[Digest] Обработка для {pillar_label}: {art['title']}")
            card_text = mentor.process_article(art)
            if card_text:
                if send_telegram_message(card_text):
                    mark_news_sent(art["link"], art["title"])
                    sent_count += 1
                    time.sleep(1)
                    break
            else:
                # Отсеянные статьи помечаем, чтобы не повторять
                mark_news_sent(art["link"], art["title"])

    print(f"[Digest] Завершено. Отправлено {sent_count}/4 тем.")
    if sent_count > 0:
        send_telegram_message(
            f"🎉 <b>Свежий дайджест доставлен ({sent_count}/4 тем)!</b>\n"
            "Выбери непонятный термин и скопируй готовый промпт в AI для закрепления. Приятного погружения!"
        )

if __name__ == "__main__":
    run_digest()
