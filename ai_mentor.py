import os
from typing import Dict, Any, Optional
from google import genai
from config import GEMINI_API_KEY

MODELS_TO_TRY = [
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite"
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
Твоя цель — отбирать ТОЛЬКО ПРАКТИЧЕСКИЕ, ПРИКЛАДНЫЕ И ЗАХВАТЫВАЮЩИЕ материалы из мира IT:
1. 🤖 ИИ, агенты и бенчмарки: сравнения моделей (Claude, GPT, DeepSeek, Gemini), кто круче кодит, LMSYS лидерборды, протокол MCP, локальные LLM (Ollama, vLLM, квантование), RAG и агентные фреймворки.
2. 🛡️ Сети, VPN и кибербезопасность: протоколы обхода блокировок и приватности (VLESS, WireGuard, Shadowsocks, Xray), борьба с DPI, реальные эксплоиты, zero-day уязвимости, разборы атак и защита инфраструктуры.
3. 🛠️ Топ инструментов, Open-Source и архитектура: крутые CLI-утилиты, топы полезного софта для разработчиков, System Design, архитектура баз данных и микросервисов.
4. 🔥 Главные мировые события и релизы в IT (прорывы гигантов, важные релизы языков/ядер).

⛔ КРИТИЧЕСКОЕ ПРАВИЛО ФИЛЬТРАЦИИ:
Если статья посвящена:
- Биологической нейрофизиологии, устройству биологического мозга человека или животных;
- Абстрактным философским рассуждениям ни о чём («заменит ли ИИ человечество», научпоп без техники и кода);
- Чисто финансовым отчетам, корпоративным сплетням и рекламной «воде» без инженерной сути
-> СТРОГО верни одно слово: SKIP (и ничего больше!).

Если статья ПРАКТИЧНАЯ, интересная для студента и полезна для профессионального кругозора, сформируй карточку в формате HTML для Telegram (используй только разрешенные теги <b>, <i>, <code>, <a href="...">).
Язык: СТРОГО русский (даже если источник англоязычный).

Формат карточки:
<b>📌 [Четкий заголовок на русском: суть технологии или новости]</b>
📂 <i>{category} • Источник: {source}</i>

<b>📝 Суть в двух словах:</b>
[2-3 емких предложения: что произошло/создано, в чем инженерная фишка и почему это важно знать]

<b>🧠 Что изучить (разбор на пальцах):</b>
1. <b>[Термин / Концепт 1]</b> — [простое объяснение в 1 предложение на пальцах, как это работает]
2. <b>[Термин / Инструмент 2]</b> — [простое объяснение в 1 предложение]
3. <b>[Термин / Паттерн 3]</b> — [простое объяснение в 1 предложение]

💡 <b>Промпт для нейросети:</b>
<code>[Готовый вопрос для нейросети, который можно скопировать в один клик и за 5 минут детально разобраться в теме с примерами или командами]</code>

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
