from flask import Flask
import threading
import telebot, requests, json, os
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot import types

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
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
    d={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",48:"Depositing rime fog",51:"Light drizzle",53:"Drizzle",55:"Dense drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",71:"Slight snow",73:"Moderate snow",75:"Heavy snow",80:"Slight showers",81:"Moderate showers",82:"Violent showers",95:"Thunderstorm",96:"Thunderstorm slight hail",99:"Thunderstorm heavy hail"}
    return d.get(code, str(code))

def get_weather(lat,lon):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_direction_10m_dominant&hourly=temperature_2m,precipitation_probability,weather_code&timezone=auto&forecast_days=7"
    return requests.get(url, timeout=10).json()

def get_air(lat,lon):
    try:
        url=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,european_aqi,pm2_5,pm10"
        return requests.get(url, timeout=10).json()
    except:
        return None

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
    loc=get_loc(m.from_user.id)
    bot.send_message(m.chat.id, f"Hello! Welcome to the Time & Weather Bot.\nI show the current time and weather for your saved location. You can also check forecasts, rain, air quality, UV levels, sunrise and sunset, wind, and weather alerts.\n\nYour saved location is ready. Use the menu below or send a command.", reply_markup=main_kb())

@bot.message_handler(content_types=['location'])
def loc_handler(m):
    try:
        d=get_weather(m.location.latitude, m.location.longitude)
        tz=d.get('timezone','Europe/Belgrade')
    except:
        tz='Europe/Belgrade'
    user_locations[str(m.from_user.id)]={"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz}
    save()
    bot.send_message(m.chat.id, f"Location saved. I'll use it for your time and weather commands.", reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def all_text(m):
    t=m.text
    if not t:
        return
    loc=get_loc(m.from_user.id)

    if t=="Back to main menu":
        bot.send_message(m.chat.id, "Main menu:", reply_markup=main_kb())
        return
    if t in ["Change location","Share my location"]:
        bot.send_message(m.chat.id, "Please share your new location using the button below.", reply_markup=loc_kb())
        return
    if t=="Show time":
        now=datetime.now(ZoneInfo(loc['timezone']))
        bot.send_message(m.chat.id, f"Current time in {loc['timezone']}:\n{now.strftime('%A, %d %B %Y at %H:%M:%S %Z')}", reply_markup=main_kb())
        return
    if t=="Help" or t=="/help":
        bot.send_message(m.chat.id, "Available commands:\n/watch - current time\n/weather - current weather\n/weekweather - 7-day forecast\n/hourly - next 24 hours\n/tomorrow - tomorrow's forecast\n/rain - rain probability\n/air - air quality\n/uv - UV index\n/sun - sunrise and sunset\n/wind - wind details\n/alerts - weather warnings\n/change_location - share a new location\n/help - show this list\n\nUse the Weather commands button for the remaining weather options.", reply_markup=main_kb())
        return
    if t=="Weather commands":
        bot.send_message(m.chat.id, "Weather commands:", reply_markup=weather_kb())
        return

    # Weather submenu
    try:
        w=get_weather(loc['lat'], loc['lon'])
    except:
        bot.send_message(m.chat.id, "Can't get weather now, try again.", reply_markup=weather_kb())
        return

    if t in ["Current weather","/weather"]:
        c=w['current']
        bot.send_message(m.chat.id, f"Weather at your saved location:\nTimezone: {w['timezone']}\n{weather_text(c['weather_code'])}\nTemperature: {c['temperature_2m']}°C\nFeels like: {c['apparent_temperature']}°C\nHumidity: {c['relative_humidity_2m']}%\nWind: {c['wind_speed_10m']} km/h", reply_markup=weather_kb())
    elif t in ["7-day forecast","/
