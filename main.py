import os, asyncio, threading
from flask import Flask
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang, set_user_lang
from bot.dst.handler import time_handler, dst_handler

BOT_TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot OK 10 lang + lang button"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

try:
    from bot.weather.handler import current_handler, today_handler, week_handler
    HAS_WEATHER = True
except:
    HAS_WEATHER = False

LANGS = {"en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская","uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski","es":"🇪🇸 Español","pl":"🇵🇱 Polski"}

def lang_keyboard():
    btns = [InlineKeyboardButton(v, callback_data=f"setlang_{k}") for k,v in LANGS.items()]
    return InlineKeyboardMarkup([btns[i:i+2] for i in range(0, len(btns), 2)])

def main_keyboard(lang_code):
    data = ALL_LANGUAGES.get(lang_code, ALL_LANGUAGES["en"])
    b = data["buttons"]
    kb = [
        [KeyboardButton(b["share"], request_location=True)],
        [KeyboardButton(b["time"]), KeyboardButton(b["dst"])],
        [KeyboardButton(b["today"]), KeyboardButton(b["week"])],
        [KeyboardButton("🌐 Language / Язык"), KeyboardButton("/current")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if lang not in ALL_LANGUAGES:
        await update.message.reply_text("👋 Choose your language / Выбери язык:", reply_markup=lang_keyboard())
        return
    data = ALL_LANGUAGES[lang]
    await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Choose language / Выбери язык:", reply_markup=lang_keyboard())

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    set_user_lang(update.effective_user.id, lang)
    data = ALL_LANGUAGES[lang]
    await query.edit_message_text(f"✅ {LANGS[lang]}")
    await context.bot.send_message(chat_id=query.message.chat_id, text=data["greeting"], reply_markup=main_keyboard(lang))

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text(f"📍 Got location! Now try /current")

def main():
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", lang_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^setlang_"))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    if HAS_WEATHER:
        app.add_handler(CommandHandler("current", current_handler))
        app.add_handler(CommandHandler("today", today_handler))
        app.add_handler(CommandHandler("week", week_handler))
    # Кнопка "Language" текстом
    app.add_handler(MessageHandler(filters.Regex("^(🌐 Language|Language|Язык)"), lang_command))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    print("Bot with language switch button!")
    app.run_polling()

if __name__ == "__main__": main()