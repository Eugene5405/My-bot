from flask import Flask
import threading
import telebot
import requests
import json
import os
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

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max,wind_speed_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
    return requests.get(url, timeout=10).json()

def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Change location", "Help", "Show time")
    kb.row("Share my location", "Weather commands")
    return kb

def weather_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Current weather", "7-day forecast")
    kb.row("Hourly", "Tomorrow")
    kb.row("Rain forecast", "Air quality")
    kb.row("UV index", "Sun times")
    kb.row("Wind", "Weather alerts")
    kb.row("Back to main menu")
    return kb

def loc_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("Share your location 📍", request_location=True))
    kb.add("Back to main menu")
    return kb

@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.send_message(m.chat.id, "Hello! Welcome to Time & Weather Bot.", reply_markup=main_kb())

@bot.message_handler(commands=['watch'])
def cmd_watch(m):
    loc = get_loc(m.from_user.id)
    now = datetime.now(ZoneInfo(loc['timezone']))
    bot.send_message(m.chat.id, f"Current time in {loc['timezone']}:\n{now.strftime('%A, %d %B %Y at %H:%M:%S')}", reply_markup=main_kb())

@bot.message_handler(commands=['weather'])
def cmd_weather(m):
    loc = get_loc(m.from_user.id)
    w = get_weather(loc['lat'], loc['lon'])
    c = w['current']
    bot.send_message(m.chat.id, f"Temp: {c['temperature_2m']}C Feels {c['apparent_temperature']}C Wind {c['wind_speed_10m']}", reply_markup=weather_kb())

@bot.message_handler(content_types=['location'])
def loc_handler(m):
    d = get_weather(m.location.latitude, m.location.longitude)
    user_locations[str(m.from_user.id)] = {"lat": m.location.latitude, "lon": m.location.longitude, "timezone": d.get('timezone','Europe/Belgrade')}
    save()
    bot.send_message(m.chat.id, "Location saved!", reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def all_text(m):
    t = (m.text or "").strip()
    if t == "Back to main menu":
        bot.send_message(m.chat.id, "Main menu:", reply_markup=main_kb())
        return
    if t in ["Change location", "Share my location"]:
        bot.send_message(m.chat.id, "Please share location", reply_markup=loc_kb())
        return
    if t == "Show time":
        loc = get_loc(m.from_user.id)
        now = datetime.now(ZoneInfo(loc['timezone']))
        bot.send_message(m.chat.id, f"Current time: {now.strftime('%A, %d %B %Y at %H:%M:%S')}", reply_markup=main_kb())
        return
    if t == "Weather commands":
        bot.send_message(m.chat.id, "Weather commands:", reply_markup=weather_kb())
        return
    if t == "Current weather":
        loc = get_loc(m.from_user.id)
        w = get_weather(loc['lat'], loc['lon'])
        c = w['current']
        bot.send_message(m.chat.id, f"Temp {c['temperature_2m']}C Humidity {c['relative_humidity_2m']}%", reply_markup=weather_kb())
        return
    if t == "Wind":
        loc = get_loc(m.from_user.id)
        w = get_weather(loc['lat'], loc['lon'])
        bot.send_message(m.chat.id, f"
