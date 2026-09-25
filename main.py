import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.greetings.start import start_handler
from bot.dst.handler import dst_handler, time_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    print("Запускаю бота...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    print("✅ Бот запущен!")
    app.run_polling()

if name == "main":
    main()
