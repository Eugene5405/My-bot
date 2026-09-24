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
user_locations={}
if os.path.exists(FILE):
 try:
  with open(FILE,'r') as f: user_locations=json.load(f)
 except: user_locations={}

def save():
 with open(FILE,'w') as f: json.dump(user_locations,f)
def get_loc(uid): return user_locations.get(str(uid),{"lat":44.8125,"lon":20.4612,"timezone":"Europe/Belgrade"})
def get_weather(lat,lon):
 url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max,wind_speed_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
 return requests.get(url,timeout=10).json()
def get_air(lat,lon):
 try:
  url=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pm2_5,pm10"
  return requests.get(url,timeout=10).json()
 except: return None

def get_dst_info(tz_name):
 try:
  tz=ZoneInfo(tz_name)
  now=datetime.now(tz)
  def is_dst(dt): return dt.dst()!=timedelta(0)
  curr=is_dst(now)
  offset=now.utcoffset()
  status="Летнее (DST)" if curr else "Зимнее (Standard)"
  # ищем следующий переход
  check=now
  for _ in range(370):
   check+=timedelta(days=1)
   check=check.replace(hour=2,minute=0,second=0,microsecond=0)
   if is_dst(check)!=curr:
    for h in range(24):
     test=check.replace(hour=h)
     if is_dst(test)!=curr:
      if is_dst(test): direction="Часы ВПЕРЕД на 1 час"
      else: direction="Часы НАЗАД на 1 час"
      return f"📍 Timezone: {tz_name}\n🕐 Сейчас: {status}\nUTC offset: {offset}\n\nСледующий переход:\n{test.strftime('%d %B %Y в %H:00')}\n{direction}\n\n{'Летом светает позже, темнеет позже' if is_dst(test) else 'Зимой светает раньше, темнеет раньше'}"
    break
  return f"📍 Timezone: {tz_name}\n🕐 Сейчас: {status}\nUTC offset: {offset}\n\nВ этой зоне нет перехода на летнее/зимнее время (как в большинстве стран у экватора или там где DST отменили)."
 except Exception as e: return f"Не удалось получить DST для {tz_name}: {e}"

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
def cmd_start(m): bot.send_message(m.chat.id,"Hello! Welcome to Time & Weather Bot.\n\nCommands:\n/watch - time\n/dst - winter/summer time info\n/weather - weather menu",reply_markup=main_kb())

@bot.message_handler(commands=['watch','time'])
def cmd_watch(m):
 loc=get_loc(m.from_user.id)
 now=datetime.now(ZoneInfo(loc['timezone']))
 dst=get_dst_info(loc['timezone'])
 bot.send_message(m.chat.id,f"Current time in {loc['timezone']}:\n{now.strftime('%A, %d %B %Y at %H:%M:%S %Z')}\n\n{dst}",reply_markup=main_kb())

@bot.message_handler(commands=['dst','dst_info','summertime','wintertime','summerwinter'])
def cmd_dst(m):
 loc=get_loc(m.from_user.id)
 dst=get_dst_info(loc['timezone'])
 now=datetime.now(ZoneInfo(loc['timezone']))
 bot.send_message(m.chat.id,f"⏰ {now.strftime('%H:%M:%S %d %B %Y')}\n\n{dst}",reply_markup=main_kb())

@bot.message_handler(content_types=['location'])
def loc_handler(m):
 d=get_weather(m.location.latitude,m.location.longitude)
 user_locations[str(m.from_user.id)]={"lat":m.location.latitude,"lon":m.location.longitude,"timezone":d.get('timezone','Europe/Belgrade')}
 save()
 dst=get_dst_info(d.get('timezone','Europe/Belgrade'))
 bot.send_message(m.chat.id,f"Location saved! {d.get('timezone')}\n\n{dst}",reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def all_text(m):
 t=(m.text or "").strip()
 if t=="Back to main menu": bot.send_message(m.chat.id,"Main menu:",reply_markup=main_kb()); return
 if t in ["Change location","Share my location"]: bot.send_message(m.chat.id,"Please share location",reply_markup=loc_kb()); return
 if t=="Show time":
  loc=get_loc(m.from_user.id); now=datetime.now(ZoneInfo(loc['timezone'])); dst=get_dst_info(loc['timezone'])
  bot.send_message(m.chat.id,f"Current time in {loc['timezone']}:\n{now.strftime('%A, %d %B %Y at %H:%M:%S %Z')}\n\n{dst}",reply_markup=main_kb()); return
 if t in ["DST info","DST","Summer/Winter time","Winter/Summer time"]:
  loc=get_loc(m.from_user.id); dst=get_dst_info(loc['timezone']); now=datetime.now(ZoneInfo(loc['timezone']))
  bot.send_message(m.chat.id,f"⏰ {now.strftime('%H:%M:%S %d %B %Y')}\n\n{dst}",reply_markup=main_kb()); return
 if t=="Help": bot.send_message(m.chat.id,"Commands:\n/watch - time\n/dst - DST info (летнее/зимнее)\n/weather - weather menu\nShare location to change timezone",reply_markup=main_kb()); return
 if t=="Weather commands": bot.send_message(m.chat.id,"Weather commands:",reply_markup=weather_kb()); return

 loc=get_loc(m.from_user.id); w=get_weather(loc['lat'],loc['lon'])
 if t=="Current weather":
  c=w['current']; txt=f"Current weather ({w['timezone']}):\nTemp: {c['temperature_2m']}C Feels: {c['apparent_temperature']}C\nHumidity: {c['relative_humidity_2m']}%\nWind: {c['wind_speed_10m']} km/h"
 elif t=="7-day forecast":
  d=w['daily']; txt="7-day:\n";
  for i in range(len(d['time'])): txt+=f"{d['time'][i]}: {d['temperature_2m_min'][i]}-{d['temperature_2m_max'][i]}C Rain {d['precipitation_probability_max'][i]}%\n"
 elif t=="Hourly":
  h=w['hourly']; txt="Next 12h:\n";
  for i in range(12): txt+=f"{h['time'][i].split('T')[1]}: {h['temperature_2m'][i]}C {h['precipitation_probability'][i]}%\n"
 elif t=="Tomorrow":
  d=w['daily']; txt=f"Tomorrow {d['time'][1]}: {d['temperature_2m_min'][1]}-{d['temperature_2m_max'][1]}C Rain {d['precipitation_probability_max'][1]}%"
 elif t=="Rain forecast":
  d=w['daily']; txt=f"Rain: Today {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}mm Tomorrow {d['precipitation_probability_max'][1]}% {d['precipitation_sum'][1]}mm"
 elif t=="Air quality":
  a=get_air(loc['lat'],loc['lon']);
  txt=f"Air AQI {a['current']['european_aqi']} PM2.5 {a['current']['pm2_5']}" if a and 'current' in a else "Air data not available"
 elif t=="UV index": txt=f"UV today {w['daily']['uv_index_max'][0]} tomorrow {w['daily']['uv_index_max'][1]}"
 elif t=="Sun times": d=w['daily']; txt=f"Sun Today {d['sunrise'][0].split('T')[1]} - {d['sunset'][0].split('T')[1]} Tomorrow {d['sunrise'][1].split('T')[1]} - {d['sunset'][1].split('T')[1]}"
 elif t=="Wind": txt=f"Wind now {w['current']['wind_speed_10m']} km/h max today {w['daily']['wind_speed_10m_max'][0]}"
 elif t=="Weather alerts":
  p=w['daily']['precipitation_probability_max'][0]; txt=f"Rain alert {p}%" if p>70 else "No alerts"
 else: return
 bot.send_message(m.chat.id,txt,reply_markup=weather_kb())

app=Flask(__name__)
@app.route('/')
def home(): return "Bot is running"
def run_web(): app.run(host='0.0.0.0',port=10000)
threading.Thread(target=run_web,daemon=True).start()
bot.infinity_polling()
