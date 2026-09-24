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

# ПОЛНЫЙ ПЕРЕВОД ВСЕГО
LANGS={
"en":{
"name":"EN English",
"welcome":"Hi! I am your personal meteorologist\n\nI show weather more accurate than iPhone\n\nWeather:\n/current - now\n/today /tomorrow /week\n/hourly /rain /wind /sun\n\nTime:\n/time /dst\n\nPress Weather commands",
"weather_btn":"Weather commands","time_btn":"Time & DST","loc_btn":"Change Location","help_btn":"Help","back":"Back","choose_lang":"Choose language:","lang_saved":"Language saved: English",
"current_btn":"Current","today_btn":"Today","tomorrow_btn":"Tomorrow","week_btn":"Week","hourly_btn":"Hourly","rain_btn":"Rain","wind_btn":"Wind","sun_btn":"Sun","uv_btn":"UV","air_btn":"Air","alerts_btn":"Alerts",
"now_txt":"Now in","feels_txt":"Feels","humidity_txt":"Humidity","wind_txt":"Wind","today_txt":"Today","tomorrow_txt":"Tomorrow","week_txt":"7 days","rain_txt":"Rain","sun_txt":"Sun","rise_txt":"Sunrise","set_txt":"Sunset"
},
"ru":{
"name":"RU Russian",
"welcome":"Privet! Ya tvoy personalny meteorolog\n\nYa pokazhu pogodu tochnee chem iPhone\n\nPogoda:\n/current - seychas\n/today - segodnya\n/tomorrow - zavtra\n/week - 7 dney\n/hourly - po chasam\n/rain /wind /sun /uv /air\n\nVremya:\n/time - tochnoe vremya\n/dst - perevod chasov\n\nNazhmi Komandy pogody vnizu",
"weather_btn":"Komandy pogody","time_btn":"Vremya i DST","loc_btn":"Smenit lokaciyu","help_btn":"Pomoshch","back":"Nazad","choose_lang":"Vyberi yazyk:","lang_saved":"Yazyk sokhranen: Russkiy",
"current_btn":"Seychas","today_btn":"Segodnya","tomorrow_btn":"Zavtra","week_btn":"Nedelya","hourly_btn":"Po chasam","rain_btn":"Dozhd","wind_btn":"Veter","sun_btn":"Solnce","uv_btn":"UV","air_btn":"Vozduh","alerts_btn":"Trevogi",
"now_txt":"Seychas v","feels_txt":"Oshchuschaetsya","humidity_txt":"Vlajnost","wind_txt":"Veter","today_txt":"Segodnya","tomorrow_txt":"Zavtra","week_txt":"7 dney","rain_txt":"Dozhd","sun_txt":"Solnce","rise_txt":"Rassvet","set_txt":"Zakat"
},
"sr":{
"name":"RS Srpski",
"welcome":"Zdravo! Ja sam tvoj licni meteorolog\n\nPokazacu vreme tacnije nego iPhone\n\nVreme:\n/current - sada\n/today - danas\n/tomorrow - sutra\n/week - 7 dana\n/hourly - po satima\n/rain /wind /sun /uv /air\n\nVreme:\n/time - tacno vreme\n/dst - pomeranje sata\n\nPritisni Vreme komande ispod",
"weather_btn":"Vreme komande","time_btn":"Vreme i DST","loc_btn":"Promeni lokaciju","help_btn":"Pomoc","back":"Nazad","choose_lang":"Izaberi jezik:","lang_saved":"Jezik sacuvan: Srpski",
"current_btn":"Trenutno","today_btn":"Danas","tomorrow_btn":"Sutra","week_btn":"Nedelja","hourly_btn":"Po satima","rain_btn":"Kisa","wind_btn":"Vetar","sun_btn":"Sunce","uv_btn":"UV","air_btn":"Vazduh","alerts_btn":"Upozorenja",
"now_txt":"Sada u","feels_txt":"Osecaj","humidity_txt":"Vlaga","wind_txt":"Vetar","today_txt":"Danas","tomorrow_txt":"Sutra","week_txt":"7 dana","rain_txt":"Kisa","sun_txt":"Sunce","rise_txt":"Izlazak","set_txt":"Zalazak"
},
"uk":{"name":"UA Ukrainian","welcome":"Pryvit!","weather_btn":"Komandy pogody","time_btn":"Chas","loc_btn":"Lokaciyu","help_btn":"Dopomoga","back":"Nazad","choose_lang":"Mova:","lang_saved":"Mova: UA","current_btn":"Zaraz","today_btn":"Syogodni","tomorrow_btn":"Zavtra","week_btn":"Tyzhden","hourly_btn":"Po godynah","rain_btn":"Doshch","wind_btn":"Viter","sun_btn":"Sonze","uv_btn":"UV","air_btn":"Povitrya","alerts_btn":"Tryvogy","now_txt":"Zaraz u","feels_txt":"Vidchuvayetsya","humidity_txt":"Vologist","wind_txt":"Viter","today_txt":"Syogodni","tomorrow_txt":"Zavtra","week_txt":"7 dniv","rain_txt":"Doshch","sun_txt":"Sonze","rise_txt":"Skhid","set_txt":"Zakhid"},
"be":{"name":"BY Belarusian","welcome":"Pryvitannie!","weather_btn":"Nadvor'e","time_btn":"Chas","loc_btn":"Lakacyya","help_btn":"Dapamoga","back":"Nazad","choose_lang":"Mova:","lang_saved":"BY","current_btn":"Zaraz","today_btn":"Syogodni","tomorrow_btn":"Zautra","week_btn":"Tydzen","hourly_btn":"Pa gadzinah","rain_btn":"Dozhdzh","wind_btn":"Vецер","sun_btn":"Sonca","uv_btn":"UV","air_btn":"Pavetra","alerts_btn":"Tryvogi","now_txt":"Zaraz u","feels_txt":"Adchuvayetstsa","humidity_txt":"Vilgost","wind_txt":"Vецер","today_txt":"Syogodni","tomorrow_txt":"Zautra","week_txt":"7 dnyon","rain_txt":"Dozhdzh","sun_txt":"Sonca","rise_txt":"Uskhod","set_txt":"Zakhad"},
"pl":{"name":"PL Polski","welcome":"Czesc!","weather_btn":"Pogoda","time_btn":"Czas","loc_btn":"Lokalizacja","help_btn":"Pomoc","back":"Wroc","choose_lang":"Jezyk:","lang_saved":"PL","current_btn":"Teraz","today_btn":"Dzis","tomorrow_btn":"Jutro","week_btn":"Tydzien","hourly_btn":"Co godzine","rain_btn":"Deszcz","wind_btn":"Wiatr","sun_btn":"Slonce","uv_btn":"UV","air_btn":"Powietrze","alerts_btn":"Alerty","now_txt":"Teraz w","feels_txt":"Odczuwalna","humidity_txt":"Wilgotnosc","wind_txt":"Wiatr","today_txt":"Dzis","tomorrow_txt":"Jutro","week_txt":"7 dni","rain_txt":"Deszcz","sun_txt":"Slonce","rise_txt":"Wschod","set_txt":"Zachod"},
"de":{"name":"DE Deutsch","welcome":"Hallo!","weather_btn":"Wetter","time_btn":"Zeit","loc_btn":"Standort","help_btn":"Hilfe","back":"Zuruck","choose_lang":"Sprache:","lang_saved":"DE","current_btn":"Jetzt","today_btn":"Heute","tomorrow_btn":"Morgen","week_btn":"Woche","hourly_btn":"Stundlich","rain_btn":"Regen","wind_btn":"Wind","sun_btn":"Sonne","uv_btn":"UV","air_btn":"Luft","alerts_btn":"Warnungen","now_txt":"Jetzt in","feels_txt":"Gefuhlt","humidity_txt":"Feuchtigkeit","wind_txt":"Wind","today_txt":"Heute","tomorrow_txt":"Morgen","week_txt":"7 Tage","rain_txt":"Regen","sun_txt":"Sonne","rise_txt":"Sonnenaufgang","set_txt":"Sonnenuntergang"},
"fr":{"name":"FR Francais","welcome":"Salut!","weather_btn":"Meteo","time_btn":"Heure","loc_btn":"Lieu","help_btn":"Aide","back":"Retour","choose_lang":"Langue:","lang_saved":"FR","current_btn":"Maintenant","today_btn":"Aujourdhui","tomorrow_btn":"Demain","week_btn":"Semaine","hourly_btn":"Horaire","rain_btn":"Pluie","wind_btn":"Vent","sun_btn":"Soleil","uv_btn":"UV","air_btn":"Air","alerts_btn":"Alertes","now_txt":"Maintenant a","feels_txt":"Ressenti","humidity_txt":"Humidite","wind_txt":"Vent","today_txt":"Aujourdhui","tomorrow_txt":"Demain","week_txt":"7 jours","rain_txt":"Pluie","sun_txt":"Soleil","rise_txt":"Lever","set_txt":"Coucher"},
"es":{"name":"ES Espanol","welcome":"Hola!","weather_btn":"Clima","time_btn":"Hora","loc_btn":"Ubicacion","help_btn":"Ayuda","back":"Atras","choose_lang":"Idioma:","lang_saved":"ES","current_btn":"Ahora","today_btn":"Hoy","tomorrow_btn":"Manana","week_btn":"Semana","hourly_btn":"Por horas","rain_btn":"Lluvia","wind_btn":"Viento","sun_btn":"Sol","uv_btn":"UV","air_btn":"Aire","alerts_btn":"Alertas","now_txt":"Ahora en","feels_txt":"Sensacion","humidity_txt":"Humedad","wind_txt":"Viento","today_txt":"Hoy","tomorrow_txt":"Manana","week_txt":"7 dias","rain_txt":"Lluvia","sun_txt":"Sol","rise_txt":"Amanecer","set_txt":"Atardecer"},
"it":{"name":"IT Italiano","welcome":"Ciao!","weather_btn":"Meteo","time_btn":"Ora","loc_btn":"Posizione","help_btn":"Aiuto","back":"Indietro","choose_lang":"Lingua:","lang_saved":"IT","current_btn":"Ora","today_btn":"Oggi","tomorrow_btn":"Domani","week_btn":"Settimana","hourly_btn":"Orario","rain_btn":"Pioggia","wind_btn":"Vento","sun_btn":"Sole","uv_btn":"UV","air_btn":"Aria","alerts_btn":"Allerte","now_txt":"Ora a","feels_txt":"Percepita","humidity_txt":"Umidita","wind_txt":"Vento","today_txt":"Oggi","tomorrow_txt":"Domani","week_txt":"7 giorni","rain_txt":"Pioggia","sun_txt":"Sole","rise_txt":"Alba","set_txt":"Tramonto"}
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
    return LANGS.get(lang,LANGS["en"]).get(key,key)

def get_w(lat,lon):
    u=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
    return requests.get(u,timeout=10).json()

def main_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(tr(uid,"weather_btn"),tr(uid,"time_btn"))
    k.row(tr(uid,"loc_btn"),"Language")
    k.row(tr(uid,"help_btn"))
    return k

def weather_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(tr(uid,"current_btn"),tr(uid,"today_btn"),tr(uid,"tomorrow_btn"))
    k.row(tr(uid,"week_btn"),tr(uid,"hourly_btn"))
    k.row(tr(uid,"rain_btn"),tr(uid,"wind_btn"))
    k.row(tr(uid,"sun_btn"),tr(uid,"uv_btn"),tr(uid,"air_btn"))
    k.row(tr(uid,"alerts_btn"),tr(uid,"back"))
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
        bot.send_message(m.chat.id, "Choose your language / Vyberi yazyk / Izaberi jezik:\n\nEN English - English\nRU Russian - Russian\nRS Srpski - Srpski\nUA Ukrainian - Ukrainian\nPL Polski - Polski\nDE Deutsch - Deutsch\nFR Francais - Francais\nES Espanol - Espanol\nIT Italiano - Italiano", reply_markup=lang_reply_kb())
        return
    welcome=LANGS.get(U.get(uid,{}).get("lang","en"),LANGS["en"])["welcome"]
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

@bot.message_handler(func=lambda m: m.text and ("EN English" in m.text or "RU Russian" in m.text or "RS Srpski" in m.text or "UA Ukrainian" in m.text or "PL Polski" in m.text or "DE Deutsch" in m.text or "FR Francais" in m.text or "ES Espanol" in m.text or "IT Italiano" in m.text or "BY Belarusian" in m.text))
def set_lang_text(m):
    txt=m.text
    code="en"
    if "RU Russian" in txt: code="ru"
    elif "RS Srpski" in txt: code="sr"
    elif "UA Ukrainian" in txt: code="uk"
    elif "PL Polski" in txt: code="pl"
    elif "DE Deutsch" in txt: code="de"
    elif "FR Francais" in txt: code="fr"
    elif "ES Espanol" in txt: code="es"
    elif "IT Italiano" in txt: code="it"
    elif "BY Belarusian" in txt: code="be"
    uid=str(m.from_user.id)
    cur=get_user(m.from_user.id)
    cur["lang"]=code
    U[uid]=cur
    save()
    bot.send_message(m.chat.id, LANGS[code]["lang_saved"], reply_markup=main_kb(uid))
    bot.send_message(m.chat.id, LANGS[code]["welcome"], reply_markup=main_kb(uid))

def get_all_btns(lang):
    d=LANGS.get(lang,LANGS["en"])
    return {
    d["current_btn"]:"current", d["today_btn"]:"today", d["tomorrow_btn"]:"tomorrow",
    d["week_btn"]:"week", d["hourly_btn"]:"hourly", d["rain_btn"]:"rain",
    d["wind_btn"]:"wind", d["sun_btn"]:"sun", d["uv_btn"]:"uv",
    d["air_btn"]:"air", d["alerts_btn"]:"alerts",
    d["weather_btn"]:"weather", d["time_btn"]:"dst", d["loc_btn"]:"location", d["help_btn"]:"help", d["back"]:"back"
    }

@bot.message_handler(commands=["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts","time","dst","location","mylocation","debug"])
def profi(m):
    uid=m.from_user.id
    s_uid=str(uid)
    lang=U.get(s_uid,{}).get("lang","en")
    L=LANGS.get(lang,LANGS["en"])
    cmd=m.text.split()[0].replace("/","")
    if cmd=="debug":
        bot.send_message(m.chat.id, f"DEBUG lang={lang} U={U.get(s_uid)}")
        return
    if cmd=="location":
        bot.send_message(m.chat.id,"Share:",reply_markup=loc_kb(uid))
        return
    loc=get_user(uid)
    w=get_w(loc["lat"],loc["lon"])
    c=w["current"]; d=w["daily"]
    txt=""
    if cmd=="current":
        txt=f"{L['now_txt']} {loc['timezone']}\n\n{L['feels_txt']}: {c['temperature_2m']}C / {c['apparent_temperature']}C\n{L['humidity_txt']}: {c['relative_humidity_2m']}%\n{L['wind_txt']}: {c['wind_speed_10m']} km/h"
    elif cmd=="today":
        txt=f"{L['today_txt']} {d['time'][0]}\n\nMax {d['temperature_2m_max'][0]}C Min {d['temperature_2m_min'][0]}C\n{L['rain_txt']}: {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}mm"
    elif cmd=="tomorrow":
        txt=f"{L['tomorrow_txt']} {d['time'][1]}\n\nMax {d['temperature_2m_max'][1]}C Min {d['temperature_2m_min'][1]}C\n{L['rain_txt']}: {d['precipitation_probability_max'][1]}%"
    elif cmd=="week":
        txt=f"{L['week_txt']}\n\n"
        for i in range(7):
            txt+=f"{d['time'][i]} {d['temperature_2m_min'][i]}C/{d['temperature_2m_max'][i]}C {d['precipitation_probability_max'][i]}%\n"
    elif cmd=="hourly":
        h=w["hourly"]; txt=f"{L['hourly_btn']}\n\n"
        for i in range(12):
            txt+=f"{h['time'][i][11:]} {h['temperature_2m'][i]}C {h['precipitation_probability'][i]}%\n"
    elif cmd=="rain":
        txt=f"{L['rain_txt']} {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}mm"
    elif cmd=="wind":
        txt=f"{L['wind_txt']} {c['wind_speed_10m']} km/h Max {d['wind_speed_10m_max'][0]}"
    elif cmd=="sun":
        txt=f"{L['sun_txt']}\n{L['rise_txt']}: {d['sunrise'][0][11:]}\n{L['set_txt']}: {d['sunset'][0][11:]}"
    elif cmd=="uv":
        txt=f"UV {d['uv_index_max'][0]}"
    elif cmd=="air":
        txt="Air data"
    elif cmd=="alerts":
        txt="No alerts"
    elif cmd=="time":
        now=datetime.now(ZoneInfo(loc["timezone"]))
        txt=f"{now}"
    elif cmd=="dst":
        txt=get_dst_info(loc["timezone"])
    elif cmd=="mylocation":
        txt=f"{loc['lat']},{loc['lon']}"
    kb=weather_kb(uid) if cmd in ["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts"] else main_kb(uid)
    bot.send_message(m.chat.id,txt,reply_markup=kb)

@bot.message_handler(func=lambda m:True)
def buttons(m):
    uid=m.from_user.id
    s_uid=str(uid)
    lang=U.get(s_uid,{}).get("lang","en")
    mapping=get_all_btns(lang)
    t=(m.text or "").strip()
    # Проверяем все кнопки на этом языке
    for btn_text, action in mapping.items():
        if t==btn_text:
            if action=="back":
                bot.send_message(m.chat.id,"Menu",reply_markup=main_kb(uid))
                return
            elif action=="weather":
                bot.send_message(m.chat.id,L["choose_lang"] if False else "Weather:",reply_markup=weather_kb(uid))
                return
            elif action=="dst":
                m.text="/dst"; return profi(m)
            elif action=="location":
                m.text="/location"; return profi(m)
            elif action=="help":
                return start(m)
            else:
                m.text=f"/{action}"; return profi(m)
    # Английские фолбэки для старых кнопок
    if "Language" in t:
        bot.send_message(m.chat.id,tr(uid,"choose_lang"),reply_markup=lang_reply_kb())
        return
    if t in ["Current","Today","Tomorrow","Week","Hourly","Rain","Wind","Sun","UV","Air","Alerts","Weather commands","Time & DST","Change Location","Help","Back"]:
        m.text=f"/{t.lower().split()[0]}"
        if "Weather" in t:
            bot.send_message(m.chat.id,"Weather:",reply_markup=weather_kb(uid))
            return
        return profi(m)
    bot.send_message(m.chat.id,"Menu",reply_markup=main_kb(uid))

app=Flask(__name__)
@app.route("/")
def home():
    return "FULL TRANSLATED OK"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_web,daemon=True).start()
while True:
    try:
        bot.infinity_polling(skip_pending=False,timeout=60)
    except Exception as e:
        print(e); time.sleep(5)
