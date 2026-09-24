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
    try:
        json.dump(U,open(FILE,"w"),ensure_ascii=False)
        print(f"SAVED: {U}")
    except Exception as e:
        print(f"SAVE ERROR: {e}")

LANGS={
"en":{"name":"EN English","welcome":"Hi! I am your personal meteorologist\n\nWeather:\n/current - now\n/today /tomorrow /week\n\nPress Weather commands below","weather_btn":"Weather commands","time_btn":"Time & DST","loc_btn":"Change Location","help_btn":"Help","back":"Back","choose_lang":"Choose language:","lang_saved":"Saved: English"},
"ru":{"name":"RU Russian","welcome":"Privet! Ya tvoy meteorolog\n\nPogoda:\n/current - seychas\n/today - segodnya\n\nNazhmi Komandy pogody","weather_btn":"Komandy pogody","time_btn":"Vremya i DST","loc_btn":"Smenit lokaciyu","help_btn":"Pomoshch","back":"Nazad","choose_lang":"Vyberi yazyk:","lang_saved":"Sokhranen: Russian"},
"sr":{"name":"RS Srpski","welcome":"Zdravo! Ja sam tvoj meteorolog\n\nPritisni Vreme komande","weather_btn":"Vreme komande","time_btn":"Vreme i DST","loc_btn":"Promeni lokaciju","help_btn":"Pomoc","back":"Nazad","choose_lang":"Izaberi jezik:","lang_saved":"Sacuvan: Srpski"},
"uk":{"name":"UA Ukrainian","welcome":"Pryvit!","weather_btn":"Komandy pogody","time_btn":"Chas","loc_btn":"Lokaciyu","help_btn":"Dopomoga","back":"Nazad","choose_lang":"Mova:","lang_saved":"Mova: UA"},
"pl":{"name":"PL Polski","welcome":"Czesc!","weather_btn":"Pogoda","time_btn":"Czas","loc_btn":"Lokalizacja","help_btn":"Pomoc","back":"Wroc","choose_lang":"Jezyk:","lang_saved":"Polski"},
"de":{"name":"DE Deutsch","welcome":"Hallo!","weather_btn":"Wetter","time_btn":"Zeit","loc_btn":"Standort","help_btn":"Hilfe","back":"Zuruck","choose_lang":"Sprache:","lang_saved":"Deutsch"},
"fr":{"name":"FR Francais","welcome":"Salut!","weather_btn":"Meteo","time_btn":"Heure","loc_btn":"Lieu","help_btn":"Aide","back":"Retour","choose_lang":"Langue:","lang_saved":"Francais"},
"es":{"name":"ES Espanol","welcome":"Hola!","weather_btn":"Clima","time_btn":"Hora","loc_btn":"Ubicacion","help_btn":"Ayuda","back":"Atras","choose_lang":"Idioma:","lang_saved":"Espanol"},
"it":{"name":"IT Italiano","welcome":"Ciao!","weather_btn":"Meteo","time_btn":"Ora","loc_btn":"Posizione","help_btn":"Aiuto","back":"Indietro","choose_lang":"Lingua:","lang_saved":"Italiano"},
"be":{"name":"BY Belarusian","welcome":"Pryvitannie!","weather_btn":"Nadvor","time_btn":"Chas","loc_btn":"Lakacyya","help_btn":"Dapamoga","back":"Nazad","choose_lang":"Mova:","lang_saved":"Belarusian"}
}

def get_user(uid):
    uid=str(uid)
    d=U.get(uid)
    if not d:
        d={"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade","lang":"en","name":"Belgrade"}
    return d

def tr(uid,key):
    uid=str(uid)
    lang=U.get(uid, {}).get("lang", "en")
    if not lang:
        lang="en"
    return LANGS.get(lang,LANGS["en"]).get(key,key)

def get_w(lat,lon):
    u=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
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
        status="Summer" if cur else "Winter"
        return f"{tz_name} {status}"
    except Exception as e:
        return str(e)

def main_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(tr(uid,"weather_btn"),tr(uid,"time_btn"))
    k.row(tr(uid,"loc_btn"),"Language")
    k.row(tr(uid,"help_btn"))
    return k

def weather_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row("Current","Today","Tomorrow")
    k.row("Week","Hourly")
    k.row("Rain","Wind")
    k.row("Sun","UV","Air")
    k.row("Alerts",tr(uid,"back"))
    return k

def lang_reply_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    k.row("EN English","RU Russian")
    k.row("RS Srpski","UA Ukrainian")
    k.row("PL Polski","DE Deutsch")
    k.row("FR Francais","ES Espanol")
    k.row("IT Italiano","BY Belarusian")
    return k

def loc_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.add(types.KeyboardButton("Share Location",request_location=True))
    k.add(tr(uid,"back"))
    return k

@bot.message_handler(commands=["start","help"])
def start(m):
    uid=str(m.from_user.id)
    if uid not in U:
        bot.send_message(m.chat.id, "Choose your language / Vyberi yazyk / Izaberi jezik:", reply_markup=lang_reply_kb())
        return
    lang=U.get(uid,{}).get("lang","en")
    welcome=LANGS.get(lang,LANGS["en"])["welcome"]
    bot.send_message(m.chat.id,welcome,reply_markup=main_kb(uid))

@bot.message_handler(commands=["lang","language"])
def cmd_lang(m):
    bot.send_message(m.chat.id,tr(m.from_user.id,"choose_lang"),reply_markup=lang_reply_kb())

@bot.message_handler(content_types=["location"])
def loc_h(m):
    w=get_w(m.location.latitude,m.location.longitude)
    tz=w.get("timezone","Europe/Belgrade")
    uid=str(m.from_user.id)
    cur=get_user(m.from_user.id)
    cur.update({"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz,"name":tz})
    U[uid]=cur
    save()
    bot.send_message(m.chat.id,f"Saved! {tz}",reply_markup=main_kb(uid))

# ОБРАБОТКА ВЫБОРА ЯЗЫКА ЧЕРЕЗ ОБЫЧНЫЕ КНОПКИ - 100% РАБОТАЕТ
@bot.message_handler(func=lambda m: m.text and ("EN English" in m.text or "RU Russian" in m.text or "RS Srpski" in m.text or "UA Ukrainian" in m.text or "PL Polski" in m.text or "DE Deutsch" in m.text or "FR Francais" in m.text or "ES Espanol" in m.text or "IT Italiano" in m.text or "BY Belarusian" in m.text))
def set_lang_text(m):
    txt=m.text
    code="en"
    if "RU Russian" in txt:
        code="ru"
    elif "RS Srpski" in txt:
        code="sr"
    elif "UA Ukrainian" in txt:
        code="uk"
    elif "PL Polski" in txt:
        code="pl"
    elif "DE Deutsch" in txt:
        code="de"
    elif "FR Francais" in txt:
        code="fr"
    elif "ES Espanol" in txt:
        code="es"
    elif "IT Italiano" in txt:
        code="it"
    elif "BY Belarusian" in txt:
        code="be"
    else:
        code="en"

    uid=str(m.from_user.id)
    cur=get_user(m.from_user.id)
    cur["lang"]=code
    U[uid]=cur
    save()
    bot.send_message(m.chat.id, LANGS[code]["lang_saved"], reply_markup=main_kb(uid))
    bot.send_message(m.chat.id, LANGS[code]["welcome"], reply_markup=main_kb(uid))

@bot.message_handler(commands=["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts","time","dst","location","mylocation","debug"])
def profi(m):
    uid=m.from_user.id
    cmd=m.text.split()[0].replace("/","")
    if cmd=="debug":
        s_uid=str(uid)
        bot.send_message(m.chat.id, f"DEBUG uid={s_uid} U={U.get(s_uid)}")
        return
    loc=get_user(uid)
    w=get_w(loc["lat"],loc["lon"])
    c=w["current"]; d=w["daily"]
    txt=""
    if cmd=="current":
        txt=f"Now {loc['timezone']} {c['temperature_2m']}C"
    elif cmd=="today":
        txt=f"Today {d['temperature_2m_max'][0]}C"
    elif cmd=="tomorrow":
        txt=f"Tomor {d['temperature_2m_max'][1]}C"
    elif cmd=="week":
        txt="7 days\n"
        for i in range(7):
            txt+=f"{d['time'][i]} {d['temperature_2m_min'][i]}C/{d['temperature_2m_max'][i]}C\n"
    elif cmd=="hourly":
        h=w["hourly"]; txt="Hourly\n"
        for i in range(6):
            txt+=f"{h['time'][i][11:]} {h['temperature_2m'][i]}C\n"
    elif cmd=="rain":
        txt=f"Rain {d['precipitation_probability_max'][0]}%"
    elif cmd=="wind":
        txt=f"Wind {c['wind_speed_10m']} km/h"
    elif cmd=="sun":
        txt=f"Sun rise {d['sunrise'][0][11:]} set {d['sunset'][0][11:]}"
    elif cmd=="uv":
        txt=f"UV {d['uv_index_max'][0]}"
    elif cmd=="air":
        a=get_air(loc["lat"],loc["lon"])
        txt=f"Air {a.get('european_aqi')}" if a else "No air"
    elif cmd=="alerts":
        txt="No alerts"
    elif cmd=="time":
        now=datetime.now(ZoneInfo(loc["timezone"]))
        txt=f"Time {now}"
    elif cmd=="dst":
        txt=get_dst_info(loc["timezone"])
    elif cmd=="location":
        bot.send_message(m.chat.id,"Share:",reply_markup=loc_kb(uid))
        return
    elif cmd=="mylocation":
        txt=f"{loc['lat']},{loc['lon']}"
    bot.send_message(m.chat.id,txt,reply_markup=weather_kb(uid) if cmd!="mylocation" else main_kb(uid))

@bot.message_handler(func=lambda m:True)
def buttons(m):
    uid=m.from_user.id
    t=(m.text or "").strip()
    if "Back" in t or "Nazad" in t or "Wroc" in t:
        bot.send_message(m.chat.id,"Menu",reply_markup=main_kb(uid)); return
    if "Weather" in t or "Pogoda" in t or "Wetter" in t or "Vreme" in t or "Meteo" in t or "Clima" in t or "Komandy" in t or "Nadvor" in t:
        bot.send_message(m.chat.id,"Weather:",reply_markup=weather_kb(uid)); return
    if "Language" in t:
        bot.send_message(m.chat.id,tr(uid,"choose_lang"),reply_markup=lang_reply_kb()); return
    if "Help" in t or "Pomosh" in t or "Pomoc" in t:
        return start(m)
    if "Location" in t or "Lokac" in t or "Share" in t:
        bot.send_message(m.chat.id,"Share:",reply_markup=loc_kb(uid)); return
    if "Time" in t or "Vremya" in t or "Vreme" in t or "Czas" in t:
        m.text="/dst"; return profi(m)
    if "Current" in t:
        m.text="/current"; return profi(m)
    if "Today" in t:
        m.text="/today"; return profi(m)
    if "Tomorrow" in t:
        m.text="/tomorrow"; return profi(m)
    if "Week" in t:
        m.text="/week"; return profi(m)
    if "Hourly" in t:
        m.text="/hourly"; return profi(m)
    if "Rain" in t:
        m.text="/rain"; return profi(m)
    if "Wind" in t:
        m.text="/wind"; return profi(m)
    if "Sun" in t:
        m.text="/sun"; return profi(m)
    if "UV" in t:
        m.text="/uv"; return profi(m)
    if "Air" in t:
        m.text="/air"; return profi(m)
    if "Alerts" in t:
        m.text="/alerts"; return profi(m)
    # Если это не команда языка - показываем меню
    if uid not in [str(k) for k in U.keys()] or m.text not in [v["name"] for v in LANGS.values()]:
        # Проверяем, может это выбор языка который не поймался
        if "English" in t or "Russian" in t or "Srpski" in t:
            return set_lang_text(m)

app=Flask(__name__)
@app.route("/")
def home():
    return "REPLY LANG OK"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_web,daemon=True).start()
while True:
    try:
        bot.infinity_polling(skip_pending=False,timeout=60)
    except Exception as e:
        print(f"POLLING ERROR: {e}")
        time.sleep(5)
