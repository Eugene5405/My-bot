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
def home(): return "Bot is running on 10 languages"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

try:
    from bot.weather.handler import current_handler, today_handler, week_handler
    HAS_WEATHER = True
except:
    HAS_WEATHER = False

LANGS = {
    "en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская",
    "uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski",
    "es":"🇪🇸 Español","pl":"🇵🇱 Polski"
}
REVERSE_LANGS = {v:k for k,v in LANGS.items()}

WEATHER_TRANS = {
    "en": ["🌤 Now","📅 Today","🌙 Tomorrow","📆 7 days","⏰ Hourly","🌧 Rain","💨 Wind","🌅 Sunrise","☀️ UV","🌫 Air","⚠️ Alerts"],
    "ru": ["🌤 Сейчас","📅 Сегодня","🌙 Завтра","📆 7 дней","⏰ По часам","🌧 Дождь","💨 Ветер","🌅 Восход","☀️ UV","🌫 Воздух","⚠️ Предупреждения"],
    "fr": ["🌤 Maintenant","📅 Aujourd'hui","🌙 Demain","📆 7 jours","⏰ Par heure","🌧 Pluie","💨 Vent","🌅 Lever","☀️ UV","🌫 Air","⚠️ Alertes"],
    "be": ["🌤 Цяпер","📅 Сёння","🌙 Заўтра","📆 7 дзён","⏰ Па гадзінах","🌧 Дождж","💨 Вецер","🌅 Усход","☀️ UV","🌫 Паветра","⚠️ Папярэджанні"],
    "uk": ["🌤 Зараз","📅 Сьогодні","🌙 Завтра","📆 7 днів","⏰ По годинах","🌧 Дощ","💨 Вітер","🌅 Схід","☀️ UV","🌫 Повітря","⚠️ Попередження"],
    "it": ["🌤 Ora","📅 Oggi","🌙 Domani","📆 7 giorni","⏰ Orario","🌧 Pioggia","💨 Vento","🌅 Alba","☀️ UV","🌫 Aria","⚠️ Avvisi"],
    "de": ["🌤 Jetzt","📅 Heute","🌙 Morgen","📆 7 Tage","⏰ Stündlich","🌧 Regen","💨 Wind","🌅 Sonnenauf","☀️ UV","🌫 Luft","⚠️ Warnungen"],
    "sr": ["🌤 Trenutno","📅 Danas","🌙 Sutra","📆 7 dana","⏰ Po satima","🌧 Kiša","💨 Vetar","🌅 Izlazak","☀️ UV","🌫 Vazduh","⚠️ Upozorenja"],
    "es": ["🌤 Ahora","📅 Hoy","🌙 Mañana","📆 7 días","⏰ Por horas","🌧 Lluvia","💨 Viento","🌅 Amanecer","☀️ UV","🌫 Aire","⚠️ Alertas"],
    "pl": ["🌤 Teraz","📅 Dziś","🌙 Jutro","📆 7 dni","⏰ Godzinowa","🌧 Deszcz","💨 Wiatr","🌅 Wschód","☀️ UV","🌫 Powietrze","⚠️ Ostrzeżenia"],
}

def clean(t): return t.split("/")[0].strip() if "/" in t else t.strip()

def lang_keyboard_bottom():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🇬🇧 English"), KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇫🇷 Français"), KeyboardButton("🇧🇾 Беларуская")],
        [KeyboardButton("🇺🇦 Українська"), KeyboardButton("🇮🇹 Italiano")],
        [KeyboardButton("🇩🇪 Deutsch"), KeyboardButton("🇷🇸 Srpski")],
        [KeyboardButton("🇪🇸 Español"), KeyboardButton("🇵🇱 Polski")],
    ], resize_keyboard=True)

def main_keyboard(lang_code):
    d = ALL_LANGUAGES.get(lang_code, ALL_LANGUAGES["en"])["buttons"]
    return ReplyKeyboardMarkup([
        [KeyboardButton(clean(d.get("share","📍 Share Location")), request_location=True)],
        [KeyboardButton(clean(d.get("weather","🌤 Weather")))],
        [KeyboardButton(clean(d.get("time","⏰ Time"))), KeyboardButton(clean(d.get("dst","⏰ DST")))],
        [KeyboardButton(clean(d.get("language","🌐 Language"))), KeyboardButton(clean(d.get("help","❓ Help")))],
    ], resize_keyboard=True)

def weather_menu(lang_code):
    t = WEATHER_TRANS.get(lang_code, WEATHER_TRANS["en"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t[0], callback_data="w_current"), InlineKeyboardButton(t[1], callback_data="w_today")],
        [InlineKeyboardButton(t[2], callback_data="w_tomorrow"), InlineKeyboardButton(t[3], callback_data="w_week")],
        [InlineKeyboardButton(t[4], callback_data="w_hourly"), InlineKeyboardButton(t[5], callback_data="w_rain")],
        [InlineKeyboardButton(t[6], callback_data="w_wind"), InlineKeyboardButton(t[7], callback_data="w_sun")],
        [InlineKeyboardButton(t[8], callback_data="w_uv"), InlineKeyboardButton(t[9], callback_data="w_air")],
        [InlineKeyboardButton(t[10], callback_data="w_alerts")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Choose language / Выбери язык:", reply_markup=lang_keyboard_bottom())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text or ""
    # Выбор языка внизу
    if txt in REVERSE_LANGS:
        lang = REVERSE_LANGS[txt]
        set_user_lang(update.effective_user.id, lang)
        data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
        await update.message.reply_text(f"✅ {txt}", reply_markup=main_keyboard(lang))
        await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))
        return
    lang = get_user_lang(update.effective_user.id)
    # Кнопка Погода / Weather на всех языках
    if any(x in txt for x in ["Погода","Weather","Météo","Wetter","Meteo","Pogoda","Clima","Vreme"]):
        await update.message.reply_text("🌤", reply_markup=weather_menu(lang))
        return
    # Время / DST
    if "DST" in txt:
        await dst_handler(update, context)
        return
    if any(x in txt for x in ["Time","Время","Zeit","Heure","Tempo","Vreme","Czas"]):
        await time_handler(update, context)
        return
    if any(x in txt for x in ["Language","Язык","Jezik","Langue","Sprache","Idioma","Język","Мова"]):
        await update.message.reply_text("🌐", reply_markup=lang_keyboard_bottom())
        return
    if any(x in txt for x in ["Help","Помощь","Aide","Hilfe","Ayuda","Pomoc"]):
        await help_command(update, context)
        return
    if HAS_WEATHER and ("Сейчас" in txt or "Now" in txt or "Jetzt" in txt):
        await current_handler(update, context)

async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cmd = q.data.replace("w_","")
    if HAS_WEATHER and cmd == "current": await current_handler(update, context)
    elif HAS_WEATHER and cmd == "today": await today_handler(update, context)
    elif HAS_WEATHER and cmd == "week": await week_handler(update, context)
    else:
        lang = get_user_lang(q.from_user.id)
        await q.message.reply_text(f"{cmd} - скоро, работают /current /today /week")

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
    app.add_handler(CommandHandler("language", lambda u,c: u.message.reply_text("🌐", reply_markup=lang_keyboard_bottom())))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    app.add_handler(CallbackQueryHandler(weather_callback, pattern="^w_"))
    if HAS_WEATHER:
        app.add_handler(CommandHandler("current", current_handler))
        app.add_handler(CommandHandler("today", today_handler))
        app.add_handler(CommandHandler("week", week_handler))
    app.add_handler(MessageHandler(filters.LOCATION, current_handler if HAS_WEATHER else help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    print("Bot started: 10 languages, big greeting, weather only after click")
    app.run_polling()

if __name__ == "__main__":
    main()