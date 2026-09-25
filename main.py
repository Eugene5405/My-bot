import os, asyncio, threading
from flask import Flask
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang, set_user_lang
from bot.dst.handler import time_handler, dst_handler

# --- ПОГОДА ИЗ ОТДЕЛЬНОЙ ПАПКИ ---
from bot.weather_menu.handler import (
    current_handler, today_handler, tomorrow_handler, week_handler,
    hourly_handler, rain_handler, wind_handler, sun_handler,
    uv_handler, air_handler, alerts_handler
)
HAS_WEATHER = True

BOT_TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot OK - 10 langs + weather bottom"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

LANGS = {
    "en":"🇬🇧 English","ru":"🇷🇺 Русский","fr":"🇫🇷 Français","be":"🇧🇾 Беларуская",
    "uk":"🇺🇦 Українська","it":"🇮🇹 Italiano","de":"🇩🇪 Deutsch","sr":"🇷🇸 Srpski",
    "es":"🇪🇸 Español","pl":"🇵🇱 Polski"
}
REVERSE_LANGS = {v:k for k,v in LANGS.items()}

BOTTOM_TRANS = {
    "en": {"share":"📍 Share Location","weather":"🌤 Weather","time":"⏰ Time","dst":"⏰ DST","lang":"🌐 Language","help":"❓ Help","back":"⬅️ Back"},
    "ru": {"share":"📍 Поделиться локацией","weather":"🌤 Погода","time":"⏰ Время","dst":"⏰ Перевод часов","lang":"🌐 Язык","help":"❓ Помощь","back":"⬅️ Назад"},
    "fr": {"share":"📍 Partager position","weather":"🌤 Météo","time":"⏰ Heure","dst":"⏰ Heure d'été","lang":"🌐 Langue","help":"❓ Aide","back":"⬅️ Retour"},
    "be": {"share":"📍 Падзяліцца","weather":"🌤 Надвор'е","time":"⏰ Час","dst":"⏰ Перавод","lang":"🌐 Мова","help":"❓ Дапамога","back":"⬅️ Назад"},
    "uk": {"share":"📍 Поділитися","weather":"🌤 Погода","time":"⏰ Час","dst":"⏰ Перевід","lang":"🌐 Мова","help":"❓ Допомога","back":"⬅️ Назад"},
    "it": {"share":"📍 Condividi pos.","weather":"🌤 Meteo","time":"⏰ Ora","dst":"⏰ Ora legale","lang":"🌐 Lingua","help":"❓ Aiuto","back":"⬅️ Indietro"},
    "de": {"share":"📍 Standort teilen","weather