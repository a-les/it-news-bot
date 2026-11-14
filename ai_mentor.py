import os
from typing import Dict, Any, Optional
from google import genai
from config import GEMINI_API_KEY

MODELS_TO_TRY = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite"
]

class AIMentor:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.client = genai.Client(api_key=api_key)

    def process_article(self, article: Dict[str, Any]) -> Optional[str]:
        title = article["title"]
        summary = article["summary"]
        source = article["source"]
        category = article["category"]
        link = article["link"]

        prompt = f"""
Ты — персональный наставник и IT-ментор для студента технического вуза.
Твоя цель — отбирать ТОЛЬКО ПРАКТИЧЕСКИЕ, ПРИКЛАДНЫЕ материалы из мира IT:
1. ИИ-агенты (AI Agents), современные LLM, агентные фреймворки (LangChain, CrewAI, AutoGen, MCP), работа с API и промптами.
2. Кибербезопасность, уязвимости, эксплоиты, zero-day, методы защиты сетей и ОС.
3. Архитектура ПО, системный дизайн (System Design), базы данных, бэкенд, DevOps, микросервисы.
4. Практические гайды, туториалы и важные события вокруг топовых технологий.

⛔ КРИТИЧЕСКОЕ ПРАВИЛО ФИЛЬТРАЦИИ:
Если статья посвящена:
- Биологической нейрофизиологии, устройству мозга человека/животных, биологии;
- Абстрактным философским рассуждениям («есть ли у ИИ сознание», научпоп без кода и практики);
- Чисто рекламному спаму или маркетинговой «воде» без технической сути
-> СТРОГО верни одно слово: SKIP (и ничего больше!).

Если статья ПРАКТИЧНАЯ и полезна для профессионального роста разработчика/безопасника, сформируй сообщение в формате HTML для Telegram (используй только теги <b>, <i>, <code>, <a>).
Язык: СТРОГО русский (даже если источник англоязычный).

Формат ответа:
<b>📌 [Заголовок на русском: четкая прикладная суть]</b>
📂 <i>{category} • Источник: {source}</i>

<b>📝 Суть в двух словах:</b>
[2-3 емких предложения: что за технология/событие/уязвимость и какая практическая польза или риск]

<b>🧠 Что изучить, чтобы понимать тему глубже:</b>
1. <b>[Термин / Концепт 1]</b> — [объяснение в 1 предложение простыми словами, как это работает на практике]
2. <b>[Термин / Инструмент 2]</b> — [объяснение в 1 предложение простыми словами]
3. <b>[Термин / Паттерн 3]</b> — [объяснение в 1 предложение простыми словами]

💡 <b>Промпт для нейросети:</b>
<code>[Готовый вопрос для нейросети, чтобы студент мог в 1 клик скопировать его и получить разбор темы с примером кода или сценарием работы]</code>

🔗 <a href="{link}">Читать первоисточник</a>

---
Новость для анализа:
Заголовок: {title}
Содержание: {summary}
"""

        for model_name in MODELS_TO_TRY:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    clean_text = response.text.strip()
                    if clean_text.upper().startswith("SKIP"):
                        print(f"[AIMentor] Пропущена непрактичная статья: '{title}'")
                        return None
                    return clean_text
            except Exception as e:
                print(f"[AIMentor] Модель {model_name} вернула ошибку: {e}. Пробуем следующую...")

        return None
