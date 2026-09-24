from flask import Flask
import threading, telebot, requests
import json, os, time
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
        with open(FILE,"r") as f:
            user_locations=json.load(f)
    except:
        user_locations={}

def save():
    with open(FILE,"w") as f:
        json.dump(user_locations,f)

def get_loc(uid):
    d={"lat":44.8125,"lon":20.4612}
    d["timezone"]="Europe/Belgrade"
    return user_locations.get(str(uid),d)

def get_weather(lat,lon):
    url="https://api.open-meteo.com/v1/forecast"
    url+=f"?latitude={lat}&longitude={lon}"
    url+="&current=temperature_2m,"
    url+="relative_humidity_2m,"
    url+="apparent_temperature,"
    url+="weather_code,wind_speed_10m"
    url+="&daily=weather_code,"
    url+="temperature_2m_max,"
    url+="temperature_2m_min,"
    url+="precipitation_sum,"
    url+="precipitation_probability_max,"
    url+="sunrise,sunset,uv_index_max,"
    url+="wind_speed_10m_max"
    url+="&hourly=temperature_2m,"
    url+="precipitation_probability"
    url+="&timezone=auto&forecast_days=7"
    return requests.get(url,timeout=10).json()

def get_air(lat,lon):
    try:
        u="https://air-quality-api.open-meteo.com"
        u+="/v1/air-quality"
        u+=f"?latitude={lat}&longitude={lon}"
        u+="&current=european_aqi,pm2_5,pm10"
        r=requests.get(u,timeout=10).json()
        if "current" in r:
            return r["current"]
    except:
        pass
    try:
        u="https://air-quality-api.open-meteo.com"
        u+="/v1/air-quality"
        u+=f"?latitude={lat}&longitude={lon}"
        u+="&hourly=european_aqi,us_aqi,"
        u+="pm2_5,pm10&timezone=auto"
        r=requests.get(u,timeout=10).json()
        if "hourly" in r:
            h=r["hourly"]
            return {
                "european_aqi":h["european_aqi"][-1],
                "us_aqi":h["us_aqi"][-1],
                "pm2_5":h["pm2_5"][-1],
                "pm10":h["pm10"][-1]
            }
    except:
        pass
    return None

def get_dst_info(tz_name):
    try:
        tz=ZoneInfo(tz_name)
        now=datetime.now(tz)
        def is_dst(dt):
            return dt.dst()!=timedelta(0)
        curr=is_dst(now)
        status="Летнее" if curr else "Зимнее"
        check=now
        for _ in range(370):
            check+=timedelta(days=1)
            check=check.replace(
                hour=2,minute=0,second=0
            )
            if is_dst(check)!=curr:
                for h in range(24):
                    test=check.replace(hour=h)
                    if is_dst(test)!=curr:
                        d="ВПЕРЕД" if is_dst(test) else "НАЗАД"
                        ds=test.strftime("%d %B %Y %H:00")
                        return f"TZ: {tz_name}\n{status}\n{ds}\n{d}"
                break
        return f"TZ: {tz_name}\n{status}\nПерехода нет."
    except Exception as e:
        return f"Ошибка {e}"

def main_kb():
    kb=types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    kb.row("Change location","Help","Show time")
    kb.row("DST info","Share my location")
    kb.row("Weather commands")
    return kb

def weather_kb():
    kb=types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    kb.row("Current weather","7-day forecast")
    kb.row("Hourly","Tomorrow")
    kb.row("Rain forecast","Air quality")
    kb.row("UV index","Sun times")
    kb.row("Wind","Weather alerts")
    kb.row("Back to main menu")
    return kb

def loc_kb():
    kb=types.ReplyKeyboardMarkup(
        resize_keyboard=True,one_time_keyboard=True
    )
    b=types.KeyboardButton(
        "Share your location",
        request_location=True
    )
    kb.add(b)
    kb.add("Back to main menu")
    return kb

@bot.message_handler(commands=["start"])
def cmd_start(m):
    bot.send_message(
        m.chat.id,"Hello!",
        reply_markup=main_kb()
    )

@bot.message_handler(commands=["watch","time"])
def cmd_watch(m):
    loc=get_loc(m.from_user.id)
    now=datetime.now(ZoneInfo(loc["timezone"]))
    dst=get_dst_info(loc["timezone"])
    bot.send_message(
        m.chat.id,
        f"Time {loc['timezone']} {now}\n\n{dst}",
        reply_markup=main_kb()
    )

@bot.message_handler(commands=["dst"])
def cmd_dst(m):
    loc=get_loc(m.from_user.id)
    dst=get_dst_info(loc["timezone"])
    bot.send_message(
        m.chat.id,dst,
        reply_markup=main_kb()
    )

@bot.message_handler(content_types=["location"])
def loc_handler(m):
    d=get_weather(m.location.latitude,m.location.longitude)
    tz=d.get("timezone","Europe/Belgrade")
    user_locations[str(m.from_user.id)]={
        "lat":m.location.latitude,
        "lon":m.location.longitude,
        "timezone":tz
    }
    save()
    dst=get_dst_info(tz)
    bot.send_message(
        m.chat.id,f"Saved {tz}\n\n{dst}",
        reply_markup=main_kb()
    )

@bot.message_handler(func=lambda m: True)
def all_text(m):
    t=(m.text or "").strip()
    if t=="Back to main menu":
        bot.send_message(
            m.chat.id,"Main menu:",
            reply_markup=main_kb()
        )
        return
    if t in ["Change location","Share my location"]:
        bot.send_message(
            m.chat.id,"Share loc",
            reply_markup=loc_kb()
        )
        return
    if t=="Show time":
        loc=get_loc(m.from_user.id)
        now=datetime.now(ZoneInfo(loc["timezone"]))
        dst=get_dst_info(loc["timezone"])
        bot.send_message(
            m.chat.id,
            f"{now}\n\n{dst}",
            reply_markup=main_kb()
        )
        return
    if t=="DST info":
        loc=get_loc(m.from_user.id)
        dst=get_dst_info(loc["timezone"])
        bot.send_message(
            m.chat.id,dst,
            reply_markup=main_kb()
        )
        return
    if t=="Help":
        bot.send_message(
            m.chat.id,"/watch /dst",
            reply_markup=main_kb()
        )
        return
    if t=="Weather commands":
        bot.send_message(
            m.chat.id,"Weather:",
            reply_markup=weather_kb()
        )
        return
    loc=get_loc(m.from_user.id)
    w=get_weather(loc["lat"],loc["lon"])
    if t=="Current weather":
        c=w["current"]
        txt=f"{w['timezone']} {c['temperature_2m']}C"
    elif t=="7-day forecast":
        d=w["daily"]
        txt="7-day:\n"
        for i in range(len(d["time"])):
            txt+=f"{d['time'][i]} {d['temperature_2m_max'][i]}C\n"
    elif t=="Hourly":
        h=w["hourly"]
        txt="Next 12h:\n"
        for i in range(12):
            txt+=f"{h['time'][i].split('T')[1]} {h['temperature_2m'][i]}C\n"
    elif t=="Tomorrow":
        d=w["daily"]
        txt=f"Tomorrow {d['time'][1]} {d['temperature_2m_max'][1]}C"
    elif t=="Rain forecast":
        d=w["daily"]
        txt=f"Rain {d['precipitation_probability_max'][0]}%"
    elif t=="Air quality":
        a=get_air(loc["lat"],loc["lon"])
        if a:
            txt=f"Air EU {a.get('european_aqi')} US {a.get('us_aqi')} PM2.5 {a.get('pm2_5')}"
        else:
            txt="Air error try later"
    elif t=="UV index":
        d=w["daily"]
        txt=f"UV {d['uv_index_max'][0]}"
    elif t=="Sun times":
        d=w["daily"]
        txt=f"Sun {d['sunrise'][0].split('T')[1]} {d['sunset'][0].split('T')[1]}"
    elif t=="Wind":
        txt=f"Wind {w['current']['wind_speed_10m']}"
    elif t=="Weather alerts":
        txt="No alerts"
    else:
        return
    bot.send_message(
        m.chat.id,txt,
        reply_markup=weather_kb()
    )

app=Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(
    target=run_web,daemon=True
app=Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(
    target=run_web,daemon=True
).start()

# защита от 409
while True:
    try:
        bot.infinity_polling(
            skip_pending=True,
            timeout=20,
            long_polling_timeout=20
        )
    except Exception as e:
        print(f"Polling error {e}")
        time.sleep(10)
        try:
            bot.remove_webhook()
        except:
            pass
        time.sleep(5)
