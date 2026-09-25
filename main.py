import os, asyncio, threading
from flask import Flask
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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

LANGS = {
    "en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская",
    "uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski",
    "es":"🇪🇸 Español","pl":"🇵🇱 Polski"
}
REVERSE_LANGS = {v:k for k,v in LANGS.items()}

# ПОЛНЫЙ ПЕРЕВОД НИЖНИХ КНОПОК НА 10 ЯЗЫКАХ
BOTTOM_TRANS = {
    "en": {"share":"📍 Share Location","weather":"🌤 Weather","time":"⏰ Time","dst":"⏰ DST","lang":"🌐 Language","help":"❓ Help","back":"⬅️ Back"},
    "ru": {"share":"📍 Поделиться локацией","weather":"🌤 Погода","time":"⏰ Время","dst":"⏰ Перевод часов","lang":"🌐 Язык","help":"❓ Помощь","back":"⬅️ Назад"},
    "fr": {"share":"📍 Partager position","weather":"🌤 Météo","time":"⏰ Heure","dst":"⏰ Heure d'été","lang":"🌐 Langue","help":"❓ Aide","back":"⬅️ Retour"},
    "be": {"share":"📍 Падзяліцца","weather":"🌤 Надвор'е","time":"⏰ Час","dst":"⏰ Перавод","lang":"🌐 Мова","help":"❓ Дапамога","back":"⬅️ Назад"},
    "uk": {"share":"📍 Поділитися","weather":"🌤 Погода","time":"⏰ Час","dst":"⏰ Перевід","lang":"🌐 Мова","help":"❓ Допомога","back":"⬅️ Назад"},
    "it": {"share":"📍 Condividi pos.","weather":"🌤 Meteo","time":"⏰ Ora","dst":"⏰ Ora legale","lang":"🌐 Lingua","help":"❓ Aiuto","back":"⬅️ Indietro"},
    "de": {"share":"📍 Standort teilen","weather":"🌤 Wetter","time":"⏰ Zeit","dst":"⏰ Zeitumst.","lang":"🌐 Sprache","help":"❓ Hilfe","back":"⬅️ Zurück"},
    "sr": {"share":"📍 Podeli lokaciju","weather":"🌤 Vreme","time":"⏰ Vreme","dst":"⏰ Pomeranje","lang":"🌐 Jezik","help":"❓ Pomoć","back":"⬅️ Nazad"},
    "es": {"share":"📍 Compartir ubic.","weather":"🌤 Clima","time":"⏰ Hora","dst":"⏰ Cambio hora","lang":"🌐 Idioma","help":"❓ Ayuda","back":"⬅️ Atrás"},
    "pl": {"share":"📍 Udostępnij lok.","weather":"🌤 Pogoda","time":"⏰ Czas","dst":"⏰ Zmiana czasu","lang":"🌐 Język","help":"❓ Pomoc","back":"⬅️ Wstecz"},
}

WEATHER_BOTTOM = {
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

def lang_keyboard_bottom():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🇬🇧 English"), KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇫🇷 Français"), KeyboardButton("🇧🇾 Беларуская")],
        [KeyboardButton("🇺🇦 Українська"), KeyboardButton("🇮🇹 Italiano")],
        [KeyboardButton("🇩🇪 Deutsch"), KeyboardButton("🇷🇸 Srpski")],
        [KeyboardButton("🇪🇸 Español"), KeyboardButton("🇵🇱 Polski")],
    ], resize_keyboard=True)

def main_keyboard(lang_code):
    t = BOTTOM_TRANS.get(lang_code, BOTTOM_TRANS["en"])
    return ReplyKeyboardMarkup([
        [KeyboardButton(t["share"], request_location=True)],
        [KeyboardButton(t["weather"])],
        [KeyboardButton(t["time"]), KeyboardButton(t["dst"])],
        [KeyboardButton(t["lang"]), KeyboardButton(t["help"])],
    ], resize_keyboard=True)

def weather_keyboard_bottom(lang_code):
    # ТЕПЕРЬ МЕНЮ ПОГОДЫ ВНИЗУ, А НЕ СВЕРХУ!
    w = WEATHER_BOTTOM.get(lang_code, WEATHER_BOTTOM["en"])
    b = BOTTOM_TRANS.get(lang_code, BOTTOM_TRANS["en"])["back"]
    return ReplyKeyboardMarkup([
        [KeyboardButton(w[0]), KeyboardButton(w[1])],
        [KeyboardButton(w[2]), KeyboardButton(w[3])],
        [KeyboardButton(w[4]), KeyboardButton(w[5])],
        [KeyboardButton(w[6]), KeyboardButton(w[7])],
        [KeyboardButton(w[8]), KeyboardButton(w[9])],
        [KeyboardButton(w[10])],
        [KeyboardButton(b)],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Choose language / Выбери язык:", reply_markup=lang_keyboard_bottom())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text or ""
    if txt in REVERSE_LANGS:
        lang = REVERSE_LANGS[txt]
        set_user_lang(update.effective_user.id, lang)
        data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
        await update.message.reply_text(f"✅ {txt}", reply_markup=main_keyboard(lang))
        await update.message.reply_text(data["greeting"], reply_markup=main_keyboard(lang))
        return

    lang = get_user_lang(update.effective_user.id)
    # Проверяем переводы
    bt = BOTTOM_TRANS.get(lang, BOTTOM_TRANS["en"])
    wb = WEATHER_BOTTOM.get(lang, WEATHER_BOTTOM["en"])

    # Кнопка назад
    if txt == bt["back"] or "Back" in txt or "Назад" in txt:
        await help_command(update, context)
        return
    # Кнопка погоды (на всех языках)
    if txt == bt["weather"]:
        await update.message.reply_text("🌤", reply_markup=weather_keyboard_bottom(lang))
        return
    # Погодные команды внизу
    if txt in wb:
        idx = wb.index(txt)
        if idx == 0 and HAS_WEATHER: await current_handler(update, context)
        elif idx == 1 and HAS_WEATHER: await today_handler(update, context)
        elif idx == 3 and HAS_WEATHER: await week_handler(update, context)
        else: await update.message.reply_text(f"{txt} - скоро подключу")
        return
    # Остальные нижние кнопки
    if txt == bt["time"]: await time_handler(update, context); return
    if txt == bt["dst"]: await dst_handler(update, context); return
    if txt == bt["lang"]: await update.message.reply_text("🌐", reply_markup=lang_keyboard_bottom()); return
    if txt == bt["help"]: await help_command(update, context); return
    if txt == bt["share"]: await update.message.reply_text("📍 Отправь локацию"); return

def main():
    try: asyncio.get_event_loop()
    except: asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    if HAS_WEATHER:
        app.add_handler(CommandHandler("current", current_handler))
        app.add_handler(CommandHandler("today", today_handler))
        app.add_handler(CommandHandler("week", week_handler))
        app.add_handler(MessageHandler(filters.LOCATION, current_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    print("Bot FIXED: weather bottom + all 10 langs")
    app.run_polling()

if __name__ == "__main__": main()