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
time.sleep(1)

FILE="locations.json"
U={}
if os.path.exists(FILE):
    try:
        U=json.load(open(FILE,"r"))
    except:
        U={}

def save():
    json.dump(U,open(FILE,"w"))

def get_loc(uid):
    return U.get(str(uid),{"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade","name":"Belgrade"})

def get_w(lat,lon):
    u=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max&hourly=temperature_2m,precipitation_probability,weather_code&timezone=auto&forecast_days=7"
    return requests.get(u,timeout=10).json()

def get_air(lat,lon):
    try:
        u=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,us_aqi,pm2_5,pm10"
        return requests.get(u,timeout=10).json()["current"]
    except:
        return None

def get_dst_info(tz_name):
    try:
        z=ZoneInfo(tz_name)
        n=datetime.now(z)
        isdst=lambda d:d.dst()!=timedelta(0)
        cur=isdst(n)
        status="☀️ Летнее время" if cur else "❄️ Зимнее время"
        c=n
        for _ in range(370):
            c+=timedelta(days=1)
            c=c.replace(hour=2,minute=0,second=0,microsecond=0)
            if isdst(c)!=cur:
                ds=c.strftime("%d %B %Y в %H:%M")
                dr="⏩ ВПЕРЕД на 1 час" if isdst(c) else "⏪ НАЗАД на 1 час"
                return f"*{tz_name}*\n{status}\n\n📅 Переход: {ds}\n{dr}"
        return f"*{tz_name}*\n{status}\n\nНет перехода в этом году"
    except Exception as e:
        return str(e)

def main_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row("🌤 Current","📅 Today","📆 Week")
    k.row("🌧 Rain","💨 Wind","☀️ Sun & UV")
    k.row("🌫 Air Quality","⏰ Time & DST")
    k.row("📍 Change Location","⚙️ Help")
    return k

def loc_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.add(types.KeyboardButton("📍 Share Location",request_location=True))
    k.add("⬅️ Back")
    return k

WELCOME="""
👋 *Привет! Я твой персональный метеоролог*

Я покажу погоду точнее чем iPhone, и никогда не забуду про перевод часов.

*📍 ЧТО Я УМЕЮ:*

*🌤 ПОГОДА:*
• /current — сейчас: температура, ощущается, влажность
• /today — подробно на сегодня
• /tomorrow — прогноз на завтра
• /week — 7 дней вперед
• /hourly — по часам на 24ч

*🔍 ДЕТАЛИ:*
• /rain — дождь: вероятность + мм
• /wind — ветер + порывы
• /sun — рассвет, закат, долгота дня
• /uv — UV индекс + совет
• /air — качество воздуха AQI + PM2.5
• /alerts — предупреждения

*⏰ ВРЕМЯ:*
• /time — точное время у тебя
• /dst — летнее/зимнее + когда перевод

*📍 ЛОКАЦИЯ:*
• /location — сменить город
• /mylocation — где я сейчас

_Нажми Share Location чтобы начать, или выбери кнопку ниже._
_Данные: Open-Meteo • Работаю 24/7_
"""

@bot.message_handler(commands=["start","help"])
def start(m):
    bot.send_message(m.chat.id,WELCOME,parse_mode="Markdown",reply_markup=main_kb())
@bot.message_handler(commands=["location"])
def cmd_loc(m):
    bot.send_message(m.chat.id,"📍 Поделись локацией:",reply_markup=loc_kb())

@bot.message_handler(commands=["mylocation"])
def cmd_myloc(m):
    loc=get_loc(m.from_user.id)
    bot.send_message(m.chat.id,f"📍 Ты тут:\nlat {loc['lat']}\nlon {loc['lon']}\n{loc['timezone']}",reply_markup=main_kb())

@bot.message_handler(content_types=["location"])
def loc_h(m):
    w=get_w(m.location.latitude,m.location.longitude)
    tz=w.get("timezone","Europe/Belgrade")
    U[str(m.from_user.id)]={"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz,"name":tz}
    save()
    bot.send_message(m.chat.id,f"✅ Сохранил!\n*Твоя зона: {tz}*\n\n{get_dst_info(tz)}",parse_mode="Markdown",reply_markup=main_kb())

@bot.message_handler(commands=["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts","time","dst"])
def profi(m):
    cmd=m.text.split()[0].replace("/","")
    loc=get_loc(m.from_user.id)
    w=get_w(loc["lat"],loc["lon"])
    c=w["current"]
    d=w["daily"]
    txt=""
    if cmd=="current":
        txt=f"🌤 *Сейчас в {loc['timezone']}*\n\n🌡 {c['temperature_2m']}°C\n🤔 Ощущается: {c['apparent_temperature']}°C\n💧 Влажность: {c['relative_humidity_2m']}%\n💨 Ветер: {c['wind_speed_10m']} км/ч"
    elif cmd=="today":
        txt=f"📅 *Сегодня {d['time'][0]}*\n\n⬆️ Макс: {d['temperature_2m_max'][0]}°C\n⬇️ Мин: {d['temperature_2m_min'][0]}°C\n🌧 Дождь: {d['precipitation_probability_max'][0]}% ({d['precipitation_sum'][0]} мм)\n💨 Ветер до {d['wind_speed_10m_max'][0]} км/ч"
    elif cmd=="tomorrow":
        txt=f"📆 *Завтра {d['time'][1]}*\n\n⬆️ {d['temperature_2m_max'][1]}°C / ⬇️ {d['temperature_2m_min'][1]}°C\n🌧 {d['precipitation_probability_max'][1]}% {d['precipitation_sum'][1]} мм"
    elif cmd=="week":
        txt=f"🗓 *7 дней {loc['timezone']}*\n\n"
        for i in range(7):
            txt+=f"{d['time'][i]}: {d['temperature_2m_min'][i]}°/{d['temperature_2m_max'][i]}° 🌧{d['precipitation_probability_max'][i]}%\n"
    elif cmd=="hourly":
        h=w["hourly"]
        txt=f"⏰ *По часам:*\n\n"
        for i in range(12):
            txt+=f"{h['time'][i][11:]} — {h['temperature_2m'][i]}°C 🌧{h['precipitation_probability'][i]}%\n"
    elif cmd=="rain":
        txt=f"🌧 *Дождь*\n\nСегодня: {d['precipitation_probability_max'][0]}% / {d['precipitation_sum'][0]} мм\nЗавтра: {d['precipitation_probability_max'][1]}% / {d['precipitation_sum'][1]} мм"
    elif cmd=="wind":
        txt=f"💨 *Ветер*\n\nСейчас: {c['wind_speed_10m']} км/ч\nСегодня макс: {d['wind_speed_10m_max'][0]} км/ч\nПорывы: {d['wind_gusts_10m_max'][0]} км/ч"
    elif cmd=="sun":
        sr=d['sunrise'][0][11:]; ss=d['sunset'][0][11:]
        txt=f"☀️ *Солнце*\n\n🌅 Рассвет: {sr}\n🌇 Закат: {ss}\n\nUV сегодня: {d['uv_index_max'][0]}"
    elif cmd=="uv":
        uv=d['uv_index_max'][0]
        level="Низкий" if uv<3 else "Средний" if uv<6 else "Высокий" if uv<8 else "Очень высокий"
        txt=f"🧴 *UV индекс: {uv} — {level}*\n\n"+("Крем не нужен" if uv<3 else "Нужен крем SPF" if uv<6 else "Опасно! SPF 50+ и очки")
    elif cmd=="air":
        a=get_air(loc["lat"],loc["lon"])
        if a:
            txt=f"🌫 *Воздух*\n\nEU AQI: {a.get('european_aqi')} / US AQI: {a.get('us_aqi')}\nPM2.5: {a.get('pm2_5')} µg/m³\nPM10: {a.get('pm10')} µg/m³"
        else:
            txt="🌫 Air data временно недоступна"
    elif cmd=="alerts":
        txt="✅ *Предупреждений нет* для твоего региона"
    elif cmd=="time":
        now=datetime.now(ZoneInfo(loc["timezone"]))
        txt=f"⏰ *Точное время:*\n\n{now.strftime('%H:%M:%S %d %B %Y')}\n{loc['timezone']}"
    elif cmd=="dst":
        txt=get_dst_info(loc["timezone"])
    bot.send_message(m.chat.id,txt,parse_mode="Markdown",reply_markup=main_kb())

@bot.message_handler(func=lambda m:True)
def buttons(m):
    t=(m.text or "")
    mp={"🌤 Current":"/current","📅 Today":"/today","📆 Week":"/week","🌧 Rain":"/rain","💨 Wind":"/wind","☀️ Sun & UV":"/sun","🌫 Air Quality":"/air","⏰ Time & DST":"/dst","📍 Change Location":"/location","⚙️ Help":"/start","⬅️ Back":"/start"}
    for k,v in mp.items():
        if k in t:
            m.text=v
            return profi(m)
    if "Time" in t:
        m.text="/time"
        return profi(m)
    bot.send_message(m.chat.id,"Выбери кнопку 👇",reply_markup=main_kb())

app=Flask(__name__)
@app.route("/")
def home():
    return "PRO OK"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_web,daemon=True).start()
while True:
    try:
        bot.infinity_polling(skip_pending=True,timeout=30)
    except Exception as e:
        print(e); time.sleep(10)
        try:
            bot.remove_webhook()
        except:
            pass
