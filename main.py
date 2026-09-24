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
    json.dump(U,open(FILE,"w"),ensure_ascii=False)

LANGS={
"en":{"name":"EN English","welcome":"Hi! I am your personal meteorologist\n\nWeather commands below","weather_btn":"Weather commands","time_btn":"Time & DST","loc_btn":"Change Location","help_btn":"Help","back":"Back","choose_lang":"Choose language:","lang_saved":"Language saved: English"},
"ru":{"name":"RU Russian","welcome":"Privet! Ya tvoy meteorolog\n\nKomandy pogody nizhe","weather_btn":"Komandy pogody","time_btn":"Vremya i DST","loc_btn":"Smenit lokaciyu","help_btn":"Pomoshch","back":"Nazad","choose_lang":"Vyberi yazyk:","lang_saved":"Yazyk sokhranen: Russian"},
"uk":{"name":"UA Ukrainian","welcome":"Pryvit! Ya tviy meteorolog","weather_btn":"Komandy pogody","time_btn":"Chas i DST","loc_btn":"Zminity lokaciyu","help_btn":"Dopomoga","back":"Nazad","choose_lang":"Obery movu:","lang_saved":"Mova: Ukrainian"},
"be":{"name":"BY Belarusian","welcome":"Pryvitannie! Ya tvoy meteoralag","weather_btn":"Nadvor'e","time_btn":"Chas","loc_btn":"Lakacyya","help_btn":"Dapamoga","back":"Nazad","choose_lang":"Vybery movu:","lang_saved":"Mova: Belarusian"},
"sr":{"name":"RS Srpski","welcome":"Zdravo! Ja sam tvoj meteorolog","weather_btn":"Vreme komande","time_btn":"Vreme i DST","loc_btn":"Promeni lokaciju","help_btn":"Pomoc","back":"Nazad","choose_lang":"Izaberi jezik:","lang_saved":"Jezik: Srpski SACUVAN"},
"pl":{"name":"PL Polski","welcome":"Czesc! Jestem twoim meteorologiem","weather_btn":"Pogoda komendy","time_btn":"Czas i DST","loc_btn":"Zmien lokalizacje","help_btn":"Pomoc","back":"Wroc","choose_lang":"Wybierz jezyk:","lang_saved":"Jezyk: Polski"},
"de":{"name":"DE Deutsch","welcome":"Hallo! Ich bin dein Meteorologe","weather_btn":"Wetter Befehle","time_btn":"Zeit & DST","loc_btn":"Standort andern","help_btn":"Hilfe","back":"Zuruck","choose_lang":"Sprache wahlen:","lang_saved":"Sprache: Deutsch GESPEICHERT"},
"fr":{"name":"FR Francais","welcome":"Salut! Je suis ton meteorologue","weather_btn":"Commandes meteo","time_btn":"Heure & DST","loc_btn":"Changer lieu","help_btn":"Aide","back":"Retour","choose_lang":"Choisis langue:","lang_saved":"Langue: Francais"},
"es":{"name":"ES Espanol","welcome":"Hola! Soy tu meteorologo","weather_btn":"Comandos clima","time_btn":"Hora y DST","loc_btn":"Cambiar ubicacion","help_btn":"Ayuda","back":"Atras","choose_lang":"Elige idioma:","lang_saved":"Idioma: Espanol"},
"it":{"name":"IT Italiano","welcome":"Ciao! Sono il tuo meteorologo","weather_btn":"Comandi meteo","time_btn":"Ora e DST","loc_btn":"Cambia posizione","help_btn":"Aiuto","back":"Indietro","choose_lang":"Scegli lingua:","lang_saved":"Lingua: Italiano"}
}

def get_user(uid):
    uid=str(uid)
    d=U.get(uid)
    if not d:
        d={"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade","lang":"en","name":"Belgrade"}
    if "lang" not in d:
        d["lang"]="en"
    return d

def tr(uid,key):
    lang=get_user(uid).get("lang","en")
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
        status="Summer time" if cur else "Winter time"
        c=n
        for _ in range(370):
            c+=timedelta(days=1)
            c=c.replace(hour=2,minute=0,second=0,microsecond=0)
            if isdst(c)!=cur:
                ds=c.strftime("%d %B %Y at %H:%M")
                dr="FORWARD 1 hour" if isdst(c) else "BACK 1 hour"
                return f"{tz_name} {status} Change: {ds} {dr}"
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

def lang_kb():
    k=types.InlineKeyboardMarkup(row_width=2)
    btns=[types.InlineKeyboardButton(info["name"],callback_data=f"lang_{code}") for code,info in LANGS.items()]
    k.add(*btns)
    return k

def loc_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.add(types.KeyboardButton("Share Location",request_location=True))
    k.add(tr(uid,"back"))
    return k

@bot.message_handler(commands=["start","help"])
def start(m):
    uid=m.from_user.id
    lang=get_user(uid).get("lang","en")
    welcome=LANGS.get(lang,LANGS["en"])["welcome"]
    bot.send_message(m.chat.id,welcome,reply_markup=main_kb(uid))

@bot.message_handler(commands=["lang","language"])
def cmd_lang(m):
    bot.send_message(m.chat.id,tr(m.from_user.id,"choose_lang"),reply_markup=lang_kb())

@bot.callback_query_handler(func=lambda c:c.data.startswith("lang_"))
def set_lang(c):
    code=c.data.replace("lang_","")
    uid=str(c.from_user.id)
    cur=get_user(c.from_user.id)
    cur["lang"]=code
    U[uid]=cur
    save()
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id,LANGS[code]["lang_saved"],reply_markup=main_kb(c.from_user.id))
    bot.send_message(c.message.chat.id,LANGS[code]["welcome"],reply_markup=main_kb(c.from_user.id))

@bot.message_handler(content_types=["location"])
def loc_h(m):
    w=get_w(m.location.latitude,m.location.longitude)
    tz=w.get("timezone","Europe/Belgrade")
    uid=str(m.from_user.id)
    cur=get_user(m.from_user.id)
    cur.update({"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz,"name":tz})
    U[uid]=cur
    save()
    bot.send_message(m.chat.id,f"Saved! {tz} {get_dst_info(tz)}",reply_markup=main_kb(m.from_user.id))

@bot.message_handler(commands=["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts","time","dst","location","mylocation"])
def profi(m):
    uid=m.from_user.id
    cmd=m.text.split()[0].replace("/","")
    loc=get_user(uid)
    w=get_w(loc["lat"],loc["lon"])
    c=w["current"]; d=w["daily"]
    txt=""
    if cmd=="current":
        txt=f"Now {loc['timezone']} {c['temperature_2m']}C feels {c['apparent_temperature']}C"
    elif cmd=="today":
        txt=f"Today {d['time'][0]} {d['temperature_2m_max'][0]}C/{d['temperature_2m_min'][0]}C Rain {d['precipitation_probability_max'][0]}%"
    elif cmd=="tomorrow":
        txt=f"Tomor {d['time'][1]} {d['temperature_2m_max'][1]}C/{d['temperature_2m_min'][1]}C"
    elif cmd=="week":
        txt="7 days\n"
        for i in range(7):
            txt+=f"{d['time'][i]} {d['temperature_2m_min'][i]}C/{d['temperature_2m_max'][i]}C {d['precipitation_probability_max'][i]}%\n"
    elif cmd=="hourly":
        h=w["hourly"]; txt="Hourly\n"
        for i in range(12):
            txt+=f"{h['time'][i][11:]} {h['temperature_2m'][i]}C {h['precipitation_probability'][i]}%\n"
    elif cmd=="rain":
        txt=f"Rain Today {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}mm"
    elif cmd=="wind":
        txt=f"Wind Now {c['wind_speed_10m']} Max {d['wind_speed_10m_max'][0]} Gust {d['wind_gusts_10m_max'][0]}"
    elif cmd=="sun":
        txt=f"Sun rise {d['sunrise'][0][11:]} set {d['sunset'][0][11:]} UV {d['uv_index_max'][0]}"
    elif cmd=="uv":
        txt=f"UV {d['uv_index_max'][0]}"
    elif cmd=="air":
        a=get_air(loc["lat"],loc["lon"])
        txt=f"Air EU:{a.get('european_aqi')} PM2.5:{a.get('pm2_5')}" if a else "Air no data"
    elif cmd=="alerts":
        txt="No alerts"
    elif cmd=="time":
        now=datetime.now(ZoneInfo(loc["timezone"]))
        txt=f"Time {now.strftime('%H:%M:%S %d %B')} {loc['timezone']}"
    elif cmd=="dst":
        txt=get_dst_info(loc["timezone"])
    elif cmd=="location":
        bot.send_message(m.chat.id,"Share:",reply_markup=loc_kb(uid))
        return
    elif cmd=="mylocation":
        txt=f"{loc['lat']},{loc['lon']} {loc['timezone']}"
    kb=weather_kb(uid) if cmd in ["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts"] else main_kb(uid)
    bot.send_message(m.chat.id,txt,reply_markup=kb)

@bot.message_handler(func=lambda m:True)
def buttons(m):
    uid=m.from_user.id
    t=(m.text or "").strip()
    if "Back" in t or "Nazad" in t or "Wroc" in t or "Zuruck" in t:
        bot.send_message(m.chat.id,"Menu",reply_markup=main_kb(uid))
        return
    if "Weather" in t or "Pogoda" in t or "Wetter" in t or "Vreme" in t or "Meteo" in t or "Clima" in t or "Komandy" in t or "Nadvor" in t:
        bot.send_message(m.chat.id,"Weather:",reply_markup=weather_kb(uid))
        return
    if "Language" in t or "Yazyk" in t or "Mova" in t or "Jezik" in t or "Jezyk" in t or "Sprache" in t:
        bot.send_message(m.chat.id,tr(uid,"choose_lang"),reply_markup=lang_kb())
        return
    if "Help" in t or "Pomosh" in t or "Dopom" in t or "Dapam" in t or "Pomoc" in t or "Hilfe" in t or "Aide" in t or "Ayuda" in t or "Aiuto" in t:
        return start(m)
    if "Location" in t or "Lokac" in t or "Lieu" in t or "Ubic" in t or "Posiz" in t or "Share" in t:
        bot.send_message(m.chat.id,"Share:",reply_markup=loc_kb(uid))
        return
    if "Time" in t or "Vremya" in t or "Chas" in t or "Vreme" in t or "Czas" in t or "Zeit" in t or "Heure" in t or "Hora" in t or "Ora" in t:
        m.text="/dst"
        return profi(m)
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
    bot.send_message(m.chat.id,"Menu",reply_markup=main_kb(uid))

app=Flask(__name__)
@app.route("/")
def home():
    return "LANG TEST OK"
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
