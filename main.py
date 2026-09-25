import os
import asyncio
import threading
from flask import Flask
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Твои файлы
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang
from bot.dst.handler import time_handler, dst_handler

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Flask чтобы Render не писал No open ports
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot is running! 10 languages OK"
def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    
    greeting = data["greeting"]
    btns = data["buttons"]
    
    # Кнопки снизу
    keyboard = [
        [KeyboardButton(btns["share"], request_location=True)],
        [KeyboardButton(btns["time"]), KeyboardButton(btns["dst"])],
        [KeyboardButton(btns["today"]), KeyboardButton(btns["week"])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(greeting, reply_markup=reply_markup)

def main():
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())
    
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKEN:
        print("ОШИБКА: Нет BOT_TOKEN")
        return

    print("Запускаю бота - 10 языков...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    
    print("Бот запущен! Готов к /start")
    app.run_polling()

if __name__ == "__main__":
    main()
