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
def home(): return "Bot OK"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

try:
    from bot.weather.handler import current_handler, today_handler, week_handler
    HAS_WEATHER = True
except:
    HAS_WEATHER = False

LANGS = {"en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская","uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski","es":"🇪🇸 Español","pl":"🇵🇱 Polski"}

def clean(text):
    return text.split("/")[0].strip() if "/" in text else text.strip()

def lang_keyboard():
    btns = [InlineKeyboardButton(v, callback_data=f"setlang_{k}") for k,v in LANGS.items()]
    return InlineKeyboardMarkup([btns[i:i+2] for i in range(0, len(btns), 2)])

def main_keyboard(lang_code):
    d = ALL_LANGUAGES.get(lang_code, ALL_LANGUAGES["en"])["buttons"]
    kb = [
        [KeyboardButton(clean(d["share"]))],
        [KeyboardButton("🌤 Weather")],
        [KeyboardButton(clean(d["time"])), KeyboardButton(clean(d["dst"]))],
        [KeyboardButton(clean(d["language"])), KeyboardButton(clean(d["help"]))],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def all_buttons_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌤 Сейчас", callback_data="w_current"), InlineKeyboardButton("📅 Сегодня", callback_data="w_today")],
        [InlineKeyboardButton("🌙 Завтра", callback_data="w_tomorrow"), InlineKeyboardButton("📆 7 дней", callback_data="w_week")],
        [InlineKeyboardButton("⏰ По часам", callback_data="w_hourly"), InlineKeyboardButton("🌧 Дождь", callback_data="w_rain")],
        [InlineKeyboardButton("💨 Ветер", callback_data="w_wind"), InlineKeyboardButton("🌅 Восход", callback_data="w_sun")],
        [InlineKeyboardButton("☀️ UV", callback_data="w_uv"), InlineKeyboardButton("🌫 Воздух", callback_data="w_air")],
        [InlineKeyboardButton("⚠️ Предупреждения", callback_data="w_alerts")],
        [InlineKeyboardButton("⏰ Time", callback_data="w_time"), InlineKeyboardButton("⏰ DST", callback_data="w_dst")],
        [InlineKeyboardButton("❓ Help", callback_data="w_help"), InlineKeyboardButton("🌐 Language", callback_data="w_lang")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Choose language / Выбери язык / Izaberi jezik:", reply_markup=lang_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    set_user_lang(q.from_user.id, lang)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await q.edit_message_text(f"✅ {LANGS[lang]}")
    await context.bot.send_message(chat_id=q.message.chat_id, text=data["greeting"], reply_markup=main_keyboard(lang))

async def weather_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌤️", reply_markup=all_buttons_menu())

async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cmd = q.data.replace("w_","")
    if cmd == "time": await time_handler(update, context)
    elif cmd == "dst": await dst_handler(update, context)
    elif cmd == "help": await help_command(update, context)
    elif cmd == "lang": await q.message.reply_text("🌐 Choose language:", reply_markup=lang_keyboard())
    elif cmd == "myloc": await q.message.reply_text("📍 Нажми кнопку Share Location внизу")
    elif HAS_WEATHER and cmd == "current": await current_handler(update, context)
    elif HAS_WEATHER and cmd == "today": await today_handler(update, context)
    elif HAS_WEATHER and cmd == "week": await week_handler(update, context)
    else: await q.message.reply_text(f"🌤️ {cmd} - скоро подключу")

def main():
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("No BOT_TOKEN")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", lambda u,c: u.message.reply_text("🌐 Choose language:", reply_markup=lang_keyboard())))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^setlang_"))
    app.add_handler(CallbackQueryHandler(weather_callback, pattern="^w_"))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    if HAS_WEATHER:
        app.add_handler(CommandHandler("current", current_handler))
        app.add_handler(CommandHandler("today", today_handler))
        app.add_handler(CommandHandler("week", week_handler))
    app.add_handler(MessageHandler(filters.Regex("Weather|Погода"), weather_button))
    app.add_handler(MessageHandler(filters.Regex("Help|Помощь"), help_command))
    app.add_handler(MessageHandler(filters.Regex("Language|Язык"), lambda u,c: u.message.reply_text("🌐 Choose language:", reply_markup=lang_keyboard())))
    print("Bot started: 10 langs + clean buttons + weather sends 🌤️")
    app.run_polling()

if __name__ == "__main__": main()