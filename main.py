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
    from bot.weather.handler import current_handler, today_handler, week_handler, tomorrow_handler, hourly_handler, rain_handler, wind_handler, sun_handler, uv_handler, air_handler, alerts_handler
    HAS_WEATHER = True
except:
    try:
        from bot.weather.handler import current_handler, today_handler, week_handler
        HAS_WEATHER = True
    except:
        HAS_WEATHER = False

LANGS = {"en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская","uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski","es":"🇪🇸 Español","pl":"🇵🇱 Polski"}

def clean(t): return t.split("/")[0].strip() if "/" in t else t.strip()

def lang_keyboard():
    btns = [InlineKeyboardButton(v, callback_data=f"setlang_{k}") for k,v in LANGS.items()]
    return InlineKeyboardMarkup([btns[i:i+2] for i in range(0, len(btns), 2)])

# --- ВСЕ КНОПКИ ВНИЗУ (как в зеленом круге) ---
def main_keyboard(lang_code):
    d = ALL_LANGUAGES.get(lang_code, ALL_LANGUAGES["en"])["buttons"]
    # Берем переводы из твоего файла, но чистим от /команд
    return ReplyKeyboardMarkup([
        [KeyboardButton(clean(d.get("share","📍 Share Location")), request_location=True)],
        [KeyboardButton("☀️ Сейчас"), KeyboardButton("📅 Сегодня")],
        [KeyboardButton("🌙 Завтра"), KeyboardButton("📆 7 дней")],
        [KeyboardButton("⏰ По часам"), KeyboardButton("🌧 Дождь")],
        [KeyboardButton("💨 Ветер"), KeyboardButton("🌅 Восход")],
        [KeyboardButton("☀️ UV"), KeyboardButton("🌫 Воздух")],
        [KeyboardButton("⚠️ Предупреждения")],
        [KeyboardButton(clean(d.get("time","⏰ Time"))), KeyboardButton(clean(d.get("dst","⏰ DST")))],
        [KeyboardButton("🌤 Погода / Weather"), KeyboardButton(clean(d.get("language","🌐 Language")))],
        [KeyboardButton(clean(d.get("help","❓ Help")))],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Choose language / Выбери язык:", reply_markup=lang_keyboard())

# --- ВОЗВРАЩАЕМ БОЛЬШОЕ ПРИВЕТСТВИЕ ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    # Это твое большое приветствие со всеми описаниями
    await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    set_user_lang(q.from_user.id, lang)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await q.edit_message_text(f"✅ {LANGS[lang]}")
    # После выбора языка сразу показываем БОЛЬШОЕ приветствие + все кнопки внизу
    await context.bot.send_message(chat_id=q.message.chat_id, text=data["greeting"], reply_markup=main_keyboard(lang))

async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text or ""
    if "Сейчас" in txt or "current" in txt.lower():
        await current_handler(update, context) if HAS_WEATHER else await update.message.reply_text("Подключи weather handler")
    elif "Сегодня" in txt or txt=="📅 Today" or "Today" in txt:
        await today_handler(update, context) if HAS_WEATHER else None
    elif "Завтра" in txt: await tomorrow_handler(update, context) if 'tomorrow_handler' in globals() else await update.message.reply_text("🌙 Завтра - скоро")
    elif "7 дней" in txt or "Week" in txt: await week_handler(update, context) if HAS_WEATHER else None
    elif "По часам" in txt: await hourly_handler(update, context) if 'hourly_handler' in globals() else await update.message.reply_text("⏰ По часам - скоро")
    elif "Дождь" in txt: await rain_handler(update, context) if 'rain_handler' in globals() else None
    elif "Ветер" in txt: await wind_handler(update, context) if 'wind_handler' in globals() else None
    elif "Восход" in txt: await sun_handler(update, context) if 'sun_handler' in globals() else None
    elif "UV" in txt: await uv_handler(update, context) if 'uv_handler' in globals() else None
    elif "Воздух" in txt: await air_handler(update, context) if 'air_handler' in globals() else None
    elif "Предупреждения" in txt: await alerts_handler(update, context) if 'alerts_handler' in globals() else None
    elif "Погода" in txt: await help_command(update, context)

def main():
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^setlang_"))
    app.add_handler(MessageHandler(filters.LOCATION, current_handler if HAS_WEATHER else help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text))
    print("Bot: ALL buttons bottom + big greeting")
    app.run_polling()

if __name__ == "__main__": main()