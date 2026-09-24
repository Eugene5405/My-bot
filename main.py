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
U={}
if os.path.exists(FILE):
    try:
        with open(FILE,"r") as f:
            U=json.load(f)
    except:
        U={}

def save():
    open(FILE,"w").write(json.dumps(U))

def get_loc(uid):
    return U.get(str(uid),{"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade"})

def get_w(lat,lon):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
    return requests.get(url,timeout=10).json()

def get_air(lat,lon):
    try:
        u=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pm2_5,pm10"
        r=requests.get(u,timeout=10).json()
        return r["current"]
    except:
        return None

def get_dst(tz_name):
    try:
        z=ZoneInfo(tz_name)
        n=datetime.now(z)
        isdst=lambda d:d.dst()!=timedelta(0)
        cur=isdst(n)
        s="Летнее" if cur else "Зимнее"
        c=n
        for _ in range(370):
            c+=timedelta(days=1)
            c=c.replace(hour=2,minute=0,second=0)
            if isdst(c)!=cur:
                ds=c.strftime("%d %B %Y")
                dr="ВПЕРЕД" if isdst(c) else "НАЗАД"
                return f"{tz_name}\n{s}\n{ds}\n{dr}"
        return f"{tz_name}\n{s}\nНет перехода"
    except Exception as e:
        return str(e)

def main_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row("Change location","Show time")
    k.row("DST info","Share my location")
    k.row("Weather commands")
    return k

def weather_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row("Current weather","7-day forecast")
    k.row("Hourly","Tomorrow")
    k.row("Rain forecast","Air quality")
    k.row("UV index","Sun times")
    k.row("Wind","Weather alerts")
    k.row("Back to main menu")
    return k

def loc_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.add(types.KeyboardButton("Share location",request_location=True))
    k.add("Back to main menu")
    return k

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id,"Hi! /watch /dst",reply_markup=main_kb())

@bot.message_handler(commands=["watch","time","dst"])
def watch(m):
    loc=get_loc(m.from_user.id)
    now=datetime.now(ZoneInfo(loc["timezone"]))
    d=get_dst(loc["timezone"])
    bot.send_message(m.chat.id,f"{now}\n\n{d}",reply_markup=main_kb())

@bot.message_handler(content_types=["location"])
def loc_h(m):
    w=get_w(m.location.latitude,m.location.longitude)
    tz=w.get("timezone","Europe/Belgrade")
    U[str(m.from_user.id)]={"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz}
    save()
    bot.send_message(m.chat.id,f"Saved {tz}\n{get_dst(tz)}",reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def all_t(m):
    t=(m.text or "").strip()
    if t=="Back to main menu":
        bot.send_message(m.chat.id,"Menu",reply_markup=main_kb())
        return
    if t=="Change location" or t=="Share my location":
        bot.send_message(m.chat.id,"Share",reply_markup=loc_kb())
        return
    if t=="Show time" or t=="DST info":
        loc=get_loc(m.from_user.id)
        now=datetime.now(ZoneInfo(loc["timezone"]))
        bot.send_message(m.chat.id,f"{now}\n{get_dst(loc['timezone'])}",reply_markup=main_kb())
        return
    if t=="Weather commands":
        bot.send_message(m.chat.id,"Weather",reply_markup=weather_kb())
        return
    loc=get_loc(m.from_user.id)
    w=get_w(loc["lat"],loc["lon"])
    txt="?"
    if t=="Current weather":
        c=w["current"]
        txt=f"{c['temperature_2m']}C feels {c['apparent_temperature']}C"
    if t=="7-day forecast":
        d=w["daily"]
        txt=""
        for i in range(7):
            txt+=f"{d['time'][i]} {d['temperature_2m_max'][i]}C\n"
    if t=="Hourly":
        h=w["hourly"]
        txt=""
        for i in range(12):
            txt+=f"{h['time'][i][11:]} {h['temperature_2m'][i]}C\n"
    if t=="Tomorrow":
        d=w["daily"]
        txt=f"{d['time'][1]} {d['temperature_2m_max'][1]}C"
    if t=="Rain forecast":
        d=w["daily"]
        txt=f"Rain {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}mm"
    if t=="Air quality":
        a=get_air(loc["lat"],loc["lon"])
        if a:
            txt=f"Air EU {a.get('european_aqi')} PM2.5 {a.get('pm2_5')} PM10 {a.get('pm10')}"
        else:
            txt="Air error try later"
    if t=="UV index":
        txt=f"UV {w['daily']['uv_index_max'][0]}"
    if t=="Sun times":
        d=w["daily"]
        txt=f"{d['sunrise'][0][11:]} - {d['sunset'][0][11:]}"
    if t=="Wind":
        txt=f"{w['current']['wind_speed_10m']} km/h"
    if t=="Weather alerts":
        txt="No alerts"
    bot.send_message(m.chat.id,txt,reply_markup=weather_kb())

app=Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_web,daemon=True).start()

while True:
    try:
        bot.infinity_polling(skip_pending=True,timeout=20)
    except Exception as e:
        print(e)
        time.sleep(10)
        try:
            bot.remove_webhook()
        except:
            pass
