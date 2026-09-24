from flask import Flask
import threading, telebot, requests, json, os, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.getenv("TOKEN")
bot=telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(2)

FILE="locations.json"
user_locations={}
if os.path.exists(FILE):
    try:
        with open(FILE,'r') as f:
            user_locations=json.load(f)
    except:
        user_locations={}

def save():
    with open(FILE,'w') as f:
        json.dump(user_locations,f)

def get_loc(uid):
    return user_locations.get(str(uid),{"lat":44.8125,"lon":20.4612,"timezone":"Europe/Belgrade"})

def get_weather(lat,lon):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max,wind_speed_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
    return requests.get(url,timeout=10).json()

def get_air(lat,lon):
    try:
        url=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,european_aqi,pm2_5,pm10,ozone,nitrogen_dioxide"
        r=requests.get(url,timeout=10).json()
        if 'current' in r:
            return r['current']
        return None
    except Exception as e:
        print(f"Air error {e}")
        return None

def get_dst_info(tz_name):
    try:
        tz=ZoneInfo(tz_name)
        now=datetime.now(tz)
        def is_dst(dt): return dt.dst()!=timedelta(0)
        curr=is_dst(now)
        offset=now.utcoffset()
        status="Летнее (DST)" if curr else "Зимнее (Standard)"
        check=now
        for _ in range(370):
            check+=timedelta(days=1)
            check=check.replace(hour=2,minute=0,second=0,microsecond=0)
            if is_dst(check)!=curr:
                for h in range(24):
                    test=check.replace(hour=h)
                    if is_dst(test)!=curr:
                        if is_dst(test):
                            direction="Часы ВПЕРЕД на 1 час"
                        else:
                            direction="Часы НАЗАД на 1 час"
                        return f"📍 Timezone: {tz_name}\n🕐 Сейчас: {status}\nUTC offset: {offset}\n\nСледующий переход:\n{test.strftime('%d %B %Y в %H:00')}\n{direction}"
                break
        return f"📍 Timezone: {tz_name}\n🕐 Сейчас: {status}\nUTC offset: {offset}\n\nВ этой зоне нет перехода на летнее/зимнее время."
    except Exception as e:
        return f"Не удалось получить DST для {tz_name}: {e}"

def main_kb():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Change location","Help","Show time")
    kb.row("DST info","Share my location")
    kb.row("Weather commands")
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
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    kb.add(types.KeyboardButton("Share your location 📍",request_location=True))
    kb.add("Back to main menu")
    return kb

@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.send_message(m.chat.id,"Hello! Welcome to Time & Weather Bot.\n\nCommands:\n/watch - time\n/dst - winter/summer time info\n/weather - weather menu",reply_markup=main_kb())

@bot.message_handler(commands=['watch','time'])
def cmd_watch(m):
    loc=get_loc(m.from_user.id)
    now=datetime.now(ZoneInfo(loc['timezone']))
    dst=get_dst_info(loc['timezone'])
    bot.send_message(m.chat.id,f"Current time in {loc['timezone']}:\n{now.strftime('%A
