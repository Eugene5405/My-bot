from flask import Flask
import threading, telebot
import requests, json
import os, time
from datetime import datetime
from datetime import timedelta
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
    default={
      "lat":44.8125,
      "lon":20.4612,
      "timezone":"Europe/Belgrade"
    }
    return user_locations.get(
        str(uid),default
    )

def get_weather(lat,lon):
    base="https://api.open-meteo.com"
    base+="/v1/forecast"
    p1=f"?latitude={lat}"
    p1+=f"&longitude={lon}"
    p2="&current=temperature_2m,"
    p2+="relative_humidity_2m,"
    p2+="apparent_temperature,"
    p2+="weather_code,"
    p2+="wind_speed_10m"
    p3="&daily=weather_code,"
    p3+="temperature_2m_max,"
    p3+="temperature_2m_min,"
    p3+="precipitation_sum,"
    p3+="precipitation_probability_max,"
    p3+="sunrise,sunset,"
    p3+="uv_index_max,"
    p3+="wind_speed_10m_max"
    p4="&hourly=temperature_2m,"
    p4+="precipitation_probability"
    p5="&timezone=auto"
    p5+="&forecast_days=7"
    url=base+p1+p2+p3+p4+p5
    return requests.get(
        url,timeout=10
    ).json()

def get_air(lat,lon):
    try:
        b="https://air-quality-api."
        b+="open-meteo.com"
        u1=f"{b}/v1/air-quality"
        u1+=f"?latitude={lat}"
        u1+=f"&longitude={lon}"
        u1+="&current=european_aqi,"
        u1+="pm2_5,pm10"
        r=requests.get(u1,timeout=10).json()
        if 'current' in r:
            cur=r['current']
            if cur.get('european_aqi')!=None:
                return cur
    except:
        pass
    try:
        u2=f"{b}/v1/air-quality"
        u2+=f"?latitude={lat}"
        u2+=f"&longitude={lon}"
        u2+="&hourly=european_aqi,"
        u2+="us_aqi,pm2_5,pm10,ozone"
        u2+="&timezone=auto"
        r=requests.get(u2,timeout=10).json()
        app=Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(
        host='0.0.0.0',
        port=10000
    )

threading.Thread(
    target=run_web,
    daemon=True
).start()

bot.infinity_polling(
    skip_pending=True
)
