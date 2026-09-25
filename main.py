import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
print("Запускаю бота...")

# Чтобы Render не ругался на порты
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой! ✅ Бот работает на Render!")

def main():
    if not BOT_TOKEN:
        print("ОШИБКА: BOT_TOKEN не найден!")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
