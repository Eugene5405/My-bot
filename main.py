import os, asyncio, threading
from flask import Flask
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang, set_user_lang
from bot.dst.handler import time_handler, dst_handler

try:
    from bot.weather_menu.handler import (
        current_handler, today_handler, tomorrow_handler, week_handler,
        hourly_handler, rain_handler, wind_handler, sun_handler,
        uv_handler, air_handler, alerts_handler
    )
except:
    from bot.weather.handler import current_handler, today_handler, week_handler
    async def tomorrow_handler(u,c): await week_handler(u,c)
    async def hourly_handler(u,c): await current_handler(u,c)
    async def rain_handler(u,c): await current_handler(u,c)
    async def wind_handler(u,c): await current_handler(u,c)
    async def sun_handler(u,c): await current_handler(u,c)
    async def uv_handler(u,c): await current_handler(u,c)
    async def air_handler(u,c): await current_handler(u,c)
    async def alerts_handler(u,c): await current_handler(u,c)

BOT_TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot OK"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

LANGS = {
    "en":"English","ru":"Russian","fr":"Francais","be":"Belaruskaya",
    "uk":"Ukrainska","it":"Italiano","de":"Deutsch","sr":"Srpski",
    "es":"Espanol","pl":"Polski"
}
REVERSE = {
    "🇬🇧 English":"en","🇷🇺 Русский":"ru","🇫🇷 Français":"fr","🇧🇾 Беларуская":"be",
    "🇺🇦 Українська":"uk","🇮🇹 Italiano":"it","🇩🇪 Deutsch":"de","🇷🇸 Srpski":"sr",
    "🇪🇸 Español":"es","🇵🇱 Polski":"pl",
    "English":"en","Russian":"ru","Deutsch":"de"
}

BOTTOM = {
    "en": {"share":"Share Location","weather":"Weather","time":"Time","dst":"DST","lang":"Language","help":"Help","back":"Back"},
    "ru": {"share":"Podpodelitsya","weather":"Pogoda","time":"Vremya","dst":"Perevod","lang":"Yazyk","help":"Pomoshch","back":"Nazad"},
    "fr": {"share":"Partager","weather":"Meteo","time":"Heure","dst":"Heure ete","lang":"Langue","help":"Aide","back":"Retour"},
    "be": {"share":"Padzyal","weather":"Nadvorje","time":"Chas","dst":"Peravod","lang":"Mova","help":"Dapamoga","back":"Nazad"},
    "uk": {"share":"Podilytysya","weather":"Pogoda","time":"Chas","dst":"Perevid","lang":"Mova","help":"Dopomoga","back":"Nazad"},
    "it": {"share":"Condividi","weather":"Meteo","time":"Ora","dst":"Ora legale","lang":"Lingua","help":"Aiuto","back":"Indietro"},
    "de": {"share":"Standort teilen","weather":"Wetter","time":"Zeit","dst":"Zeitumst","lang":"Sprache","help":"Hilfe","back":"Zurueck"},
    "sr": {"share":"Podeli lokaciju","weather":"Vreme","time":"Vreme","dst":"Pomeranje","lang":"Jezik","help":"Pomoc","back":"Nazad"},
    "es": {"share":"Compartir","weather":"Clima","time":"Hora","dst":"Cambio","lang":"Idioma","help":"Ayuda","back":"Atras"},
    "pl": {"share":"Udostepnij","weather":"Pogoda","time":"Czas","dst":"Zmiana","lang":"Jezyk","help":"Pomoc","back":"Wstecz"},
}

WEATHER_BT = {
    "en": ["Now","Today","Tomorrow","7 days","Hourly","Rain","Wind","Sunrise","UV","Air","Alerts"],
    "ru": ["Sejchas","Segodnya","Zavtra","7 dnej","Po chasam","Dozhd","Veter","Voshod","UV","Vozduh","Predupr"],
    "fr": ["Maintenant","Aujourd","Demain","7 jours","Par heure","Pluie","Vent","Lever","UV","Air","Alertes"],
    "be": ["Tsyaper","Syonnya","Zawtra","7 dzyon","Pa gadzinah","Dozhdzh","Vetser","Ushod","UV","Pavetra","Papyar"],
    "uk": ["Zaraz","Syogodni","Zavtra","7 dniv","Po godynah","Doshch","Viter","Shid","UV","Povitrya","Popered"],
    "it": ["Ora","Oggi","Domani","7 giorni","Orario","Pioggia","Vento","Alba","UV","Aria","Avvisi"],
    "de": ["Jetzt","Heute","Morgen","7 Tage","Stuendlich","Regen","Wind","Sonnenauf","UV","Luft","Warnungen"],
    "sr": ["Trenutno","Danas","Sutra","7 dana","Po satima","Kisa","Vetar","Izlazak","UV","Vazduh","Upozorenja"],
    "es": ["Ahora","Hoy","Manana","7 dias","Por horas","Lluvia","Viento","Amanecer","UV","Aire","Alertas"],
    "pl": ["Teraz","Dzis","Jutro","7 dni","Godzinowa","Deszcz","Wiatr","Wschod","UV","Powietrze","Ostrzezenia"],
}

def lang_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🇬🇧 English"), KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇫🇷 Français"), KeyboardButton("🇧🇾 Беларуская")],
        [KeyboardButton("🇺🇦 Українська"), KeyboardButton("🇮🇹 Italiano")],
        [KeyboardButton("🇩🇪 Deutsch"), KeyboardButton("🇷🇸 Srpski")],
        [KeyboardButton("🇪🇸 Español"), KeyboardButton("🇵🇱 Polski")],
    ], resize_keyboard=True)

def main_kb(lang):
    t = BOTTOM.get(lang, BOTTOM["en"])
    return ReplyKeyboardMarkup([
        [KeyboardButton("Share Location", request_location=True)],
        [KeyboardButton(t["weather"])],
        [KeyboardButton(t["time"]), KeyboardButton(t["dst"])],
        [KeyboardButton(t["lang"]), KeyboardButton(t["help"])],
    ], resize_keyboard=True)

def weather_kb(lang):
    w = WEATHER_BT.get(lang, WEATHER_BT["en"])
    b = BOTTOM.get(lang, BOTTOM["en"])["back"]
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
    await update.message.reply_text("Choose language:", reply_markup=lang_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    await update.message.reply_text(data["greeting"], reply_markup=main_kb(lang))

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()
    if txt in REVERSE:
        lang = REVERSE[txt]
        set_user_lang(update.effective_user.id, lang)
        data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
        await update.message.reply_text(f"OK {txt}", reply_markup=main_kb(lang))
        await update.message.reply_text(data["greeting"], reply_markup=main_kb(lang))
        return
    lang = get_user_lang(update.effective_user.id)
    bt = BOTTOM.get(lang, BOTTOM["en"])
    wb = WEATHER_BT.get(lang, WEATHER_BT["en"])

    if txt.lower() in ["back","nazad","retour","zurueck","atras","wstecz","indietro"]:
        await help_cmd(update, context); return
    if txt.lower() in [v.lower() for v in BOTTOM[lang].values() if "weather" in v.lower() or "pogoda" in v.lower() or "wetter" in v.lower() or "meteo" in v.lower() or "clima" in v.lower() or "vreme" in v.lower()]:
        await update.message.reply_text("Weather:", reply_markup=weather_kb(lang)); return
    # прямое совпадение кнопки погоды
    for l in BOTTOM.values():
        if txt == l["weather"]:
            await update.message.reply_text("Weather:", reply_markup=weather_kb(lang)); return

    if txt in wb:
        i = wb.index(txt)
        if i==0: await current_handler(update, context)
        elif i==1: await today_handler(update, context)
        elif i==2: await tomorrow_handler(update, context)
        elif i==3: await week_handler(update, context)
        elif i==4: await hourly_handler(update, context)
        elif i==5: await rain_handler(update, context)
        elif i==6: await wind_handler(update, context)
        elif i==7: await sun_handler(update, context)
        elif i==8: await uv_handler(update, context)
        elif i==9: await air_handler(update, context)
        elif i==10: await alerts_handler(update, context)
        return

    if txt == bt["time"]: await time_handler(update, context); return
    if txt == bt["dst"]: await dst_handler(update, context); return
    if txt == bt["lang"]: await update.message.reply_text("Lang:", reply_markup=lang_keyboard()); return
    if txt == bt["help"]: await help_cmd(update, context); return
    if "Share" in txt or "location" in txt.lower(): await update.message.reply_text("Send location"); return

    # если текст содержит слово погода на любом языке
    if txt.lower() in ["pogoda","weather","wetter","meteo","clima","vreme"]:
        await update.message.reply_text("Weather:", reply_markup=weather_kb(lang)); return

    if update.message.location:
        context.user_data["lat"]=update.message.location.latitude
        context.user_data["lon"]=update.message.location.longitude
        await current_handler(update, context); return

def main():
    try: asyncio.get_event_loop()
    except: asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("time", time_handler))
    app.add_handler(CommandHandler("dst", dst_handler))
    app.add_handler(CommandHandler("current", current_handler))
    app.add_handler(MessageHandler(filters.LOCATION, current_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("Bot fixed no emoji")
    app.run_polling()

if __name__=="__main__": main()