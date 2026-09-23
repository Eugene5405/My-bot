from flask import Flask
import threading
import telebot, requests, json, os
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot import types

TOKEN = "7627951094:AAFEwrJUkerL_641Zm1NHWOr5GU_meefBrA"
bot = telebot.TeleBot(TOKEN)

FILE = "locations.json"
user_locations = {}
if os.path.exists(FILE):
    try:
        with open(FILE, 'r') as f:
            user_locations = json.load(f)
    except:
        user_locations = {}

def save():
    with open(FILE, 'w') as f:
        json.dump(user_locations, f)

def get_loc(uid):
    return user_locations.get(str(uid), {"lat":44.8125,"lon":20.4612,"timezone":"Europe/Belgrade"})

def weather_text(code):
    d={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",80:"Showers",95:"Thunderstorm"}
    return d.get(code, str(code))

def get_weather(lat,lon):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max,wind_speed_10m_max&hourly=temperature_2m&timezone=auto&forecast_days=7"
    return requests.get(url, timeout=10).json()

def main_kb():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Change location","Help","Show time")
    kb.row("Share my location","Weather commands")
    return kb

def weather_kb():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Current weather","7-day forecast")
    kb.row("Hourly","Tomorrow")
    kb.row("Rain forecast","Air quality")
    kb.row("UV index","Sun times")
    kb.row("Wind","Weather alerts")
    kb.row("Back to main menu")
    return kb

def loc_kb():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("Share your location 📍", request_location=True))
    kb.add("Back to main menu")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Hello! Welcome to the Time & Weather Bot.\nYour saved location is ready. Use the menu below.", reply_markup=main_kb())

@bot.message_handler(commands=['help','watch','weather'])
def cmds(m):
    if m.text=='/help':
        bot.send_message(m.chat.id, "/watch - time\n/weather - weather\n/weekweather - 7 day\n/hourly\n/tomorrow\n/rain\n/air\n/uv\n/sun\n/wind\n/alerts", reply_markup=main_kb())
    elif m.text=='/watch':
        loc=get_loc(m.from_user.id)
        now=datetime.now(ZoneInfo(loc['timezone']))
        bot.send_message(m.chat.id, f"Current time in {loc['timezone']}:\n{now.strftime('%A, %d %B %Y at %H:%M:%S')}", reply_markup=main_kb())
    else:
        send_weather(m)

def send_weather(m):
    loc=get_loc(m.from_user.id)
    d=get_weather(loc['lat'],loc['lon'])
    c=d['current']
    bot.send_message(m.chat.id, f"Weather:\n{weather_text(c['weather_code'])}\nTemp: {c['temperature_2m']}C\nFeels: {c['apparent_temperature']}C\nHumidity: {c['relative_humidity_2m']}%\nWind: {c['wind_speed_10m']} km/h\nTimezone: {d['timezone']}", reply_markup=weather_kb())

@bot.message_handler(content_types=['location'])
def loc_handler(m):
    d=get_weather(m.location.latitude, m.location.longitude)
    user_locations[str(m.from_user.id)]={"lat":m.location.latitude,"lon":m.location.longitude,"timezone":d.get('timezone','Europe/Belgrade')}
    save()
    bot.send_message(m.chat.id, "Location saved!", reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def all_text(m):
    t=m.text
  app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()
