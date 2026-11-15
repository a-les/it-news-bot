import asyncio
import logging
import os
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import (
    TELEGRAM_BOT_TOKEN,
    HTTP_PROXY,
    HTTPS_PROXY,
    MORNING_HOUR,
    EVENING_HOUR
)
from database import (
    init_db,
    add_subscriber,
    get_active_subscribers,
    mark_news_sent
)
from rss_fetcher import fetch_curated_digest_candidates
from ai_mentor import AIMentor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Временная зона пользователя (UTC+6)
BOT_TIMEZONE = os.getenv("BOT_TIMEZONE", "Etc/GMT-6")

# Прокси для стабильного соединения с api.telegram.org (если запускается локально)
proxy_url = HTTPS_PROXY or HTTP_PROXY
session = AiohttpSession(proxy=proxy_url) if proxy_url else None

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    session=session,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=BOT_TIMEZONE)
mentor = AIMentor()

# Меню кнопок
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☕ Свежий дайджест")],
        [KeyboardButton(text="⚙️ Расписание"), KeyboardButton(text="❓ Как учиться")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    add_subscriber(
        chat_id=message.chat.id,
        username=user.username or "",
        first_name=user.first_name or ""
    )

    welcome_text = (
        f"👋 <b>Привет, {user.first_name or 'будущий сеньор'}!</b>\n\n"
        "Я твой персональный <b>IT & AI Mentor</b>. Моя задача — превратить лавину новостей в понятную систему обучения.\n\n"
        "<b>Каждый выпуск содержит 4 ключевые сферы:</b>\n"
        "1. 🔥 <b>Главное мировое событие</b> (Топ Hacker News, релизы гигантов);\n"
        "2. 🤖 <b>ИИ-агенты и технологии</b> (Агенты, фреймворки, как подключать);\n"
        "3. 🛡️ <b>Кибербезопасность</b> (Реальные уязвимости, нулевой день, защита);\n"
        "4. 🛠️ <b>Инженерия и Архитектура</b> (Системный дизайн, паттерны, базы данных).\n\n"
        "<i>Под каждой темой — 2–3 термина и готовый промпт для нейросети!</i>\n\n"
        f"⏰ <b>Авто-дайджесты:</b> в {MORNING_HOUR:02d}:00 (под кофе) и в {EVENING_HOUR:02d}:00.\n"
        "Или жми кнопку ниже в любое удобное время!"
    )
    await message.answer(welcome_text, reply_markup=main_kb)

async def generate_and_send_digest(chat_id: int):
    status_msg = await bot.send_message(
        chat_id,
        "🔍 <i>Отбираю топовые материалы по 4 ключевым сферам IT...</i>"
    )

    try:
        candidates_by_pillar = fetch_curated_digest_candidates()

        pillars = [
            ("fire", "🔥 Главное событие в мировом IT"),
            ("ai", "🤖 ИИ-агенты и технологии"),
            ("sec", "🛡️ Кибербезопасность"),
            ("eng", "🛠️ Инженерия и Архитектура")
        ]

        sent_count = 0

        for pillar_key, pillar_label in pillars:
            articles = candidates_by_pillar.get(pillar_key, [])
            for art in articles:
                card_text = mentor.process_article(art)
                if card_text:
                    await bot.send_message(
                        chat_id,
                        card_text,
                        disable_web_page_preview=True
                    )
                    mark_news_sent(art["link"], art["title"])
                    sent_count += 1
                    await asyncio.sleep(0.5)
                    break
                else:
                    mark_news_sent(art["link"], art["title"])

        if sent_count > 0:
            await status_msg.delete()
            await bot.send_message(
                chat_id,
                f"🎉 <b>Свежий выпуск готов ({sent_count}/4 тем)!</b>\n"
                "Выбери непонятный термин и скопируй готовый промпт в AI для закрепления. Приятного погружения!"
            )
        else:
            await status_msg.edit_text(
                "😴 <b>Пока нет новых непрочитанных топ-новостей.</b>\n"
                "Все текущие топовые темы уже были разобраны. Загляните чуть позже!"
            )

    except Exception as e:
        logger.error(f"Ошибка формирования дайджеста для {chat_id}: {e}", exc_info=True)
        await status_msg.edit_text("⚠️ Произошла ошибка при обработке новостей. Пожалуйста, попробуйте позже.")

@dp.message(F.text == "☕ Свежий дайджест")
@dp.message(Command("digest"))
async def handle_digest(message: Message):
    add_subscriber(message.chat.id, message.from_user.username or "", message.from_user.first_name or "")
    await generate_and_send_digest(message.chat.id)

@dp.message(F.text == "⚙️ Расписание")
@dp.message(Command("schedule"))
async def handle_schedule(message: Message):
    subs = get_active_subscribers()
    text = (
        "⚙️ <b>Настройки расписания:</b>\n\n"
        f"☕ <b>Утренний выпуск:</b> {MORNING_HOUR:02d}:00\n"
        f"🌆 <b>Вечерний выпуск:</b> {EVENING_HOUR:02d}:00\n\n"
        f"👥 Активных подписчиков: {len(subs)}\n"
        "💡 В любое другое время вы всегда можете нажать <b>«☕ Свежий дайджест»</b>!"
    )
    await message.answer(text)

@dp.message(F.text == "❓ Как учиться")
@dp.message(Command("help"))
async def handle_help(message: Message):
    text = (
        "💡 <b>Методика обучения по новостям (Reverse Learning):</b>\n\n"
        "1. <b>Не пытайся объять всё.</b> IT бесконечно. Каждая карточка — это сигнал о том, что реально происходит прямо сейчас.\n"
        "2. <b>Разбирай термины.</b> Под новостью даны 2–3 фундаментальных концепта. Прочитай их краткое определение.\n"
        "3. <b>Копируй готовый промпт.</b> Нажми на текст в рамке — он скопируется в буфер обмена. Вставь в ChatGPT, Claude или Gemini и пообщайся 5 минут.\n"
        "4. <b>Всего 1 дайджест в день</b> даст мощный фундамент и уберёт страх «я ничего не понимаю в IT» уже через месяц."
    )
    await message.answer(text)

async def scheduled_broadcast():
    logger.info("Запуск рассылки по расписанию...")
    subscribers = get_active_subscribers()
    for chat_id in subscribers:
        try:
            await generate_and_send_digest(chat_id)
        except Exception as e:
            logger.error(f"Не удалось отправить авто-дайджест пользователю {chat_id}: {e}")

async def main():
    init_db()

    # Запуск легкого health-check сервера для Render.com
    port = os.getenv("PORT")
    if port:
        async def handle_ping(request):
            return web.Response(text="IT Mentor Bot is running 24/7!")

        app = web.Application()
        app.router.add_get("/", handle_ping)
        app.router.add_get("/health", handle_ping)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(port))
        await site.start()
        logger.info(f"Healthcheck веб-сервер запущен на порту {port}")

    # Настройка планировщика (утро и вечер по часовому поясу пользователя)
    scheduler.add_job(
        scheduled_broadcast,
        trigger="cron",
        hour=MORNING_HOUR,
        minute=0,
        timezone=BOT_TIMEZONE,
        id="morning_digest"
    )
    scheduler.add_job(
        scheduled_broadcast,
        trigger="cron",
        hour=EVENING_HOUR,
        minute=0,
        timezone=BOT_TIMEZONE,
        id="evening_digest"
    )
    scheduler.start()
    logger.info(f"Планировщик запущен: рассылки в {MORNING_HOUR:02d}:00 и {EVENING_HOUR:02d}:00 ({BOT_TIMEZONE})")

    logger.info("Бот запущен и ожидает сообщений...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
