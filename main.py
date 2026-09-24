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
        U=json.load(open(FILE,"r",encoding="utf-8"))
    except:
        U={}

def save():
    json.dump(U,open(FILE,"w",ensure_ascii=False),ensure_ascii=False)

LANGS={
"en":{
"name":"🇬🇧 EN English",
"welcome":"Hi! I'm your personal meteorologist\n\nMore accurate than iPhone\n\n/weather commands below",
"weather_btn":"⛅ Weather","time_btn":"🕐 Time & DST","loc_btn":"📍 Location","help_btn":"❓ Help","back":"⬅️ Back","choose_lang":"Choose language:","lang_saved":"✅ Language: English",
"current_btn":"📍 Сейчас","today_btn":"📅 Сегодня","tomorrow_btn":"➡️ Завтра","week_btn":"📆 Неделя","hourly_btn":"⏰ По часам","rain_btn":"🌧 Дождь","wind_btn":"💨 Ветер","sun_btn":"🌅 Солнце","uv_btn":"☀️ UV","air_btn":"🌿 Воздух","alerts_btn":"⚠️ Тревоги",
"now_txt":"Сейчас в","feels_txt":"Ощущается","humidity_txt":"Влажность","wind_txt":"Ветер","today_txt":"Сегодня","tomorrow_txt":"Завтра","week_txt":"7 дней"
},
"ru":{
"name":"🇷🇺 RU Русский",
"welcome":"Привет! Я твой личный метеоролог\n\nПоказываю погоду точнее чем iPhone\n\nНажми ⛅ Погода внизу\n\nКоманды:\n/current - сейчас\n/today - сегодня\n/tomorrow - завтра\n/week - 7 дней\n\nВремя:\n/time /dst - перевод часов",
"weather_btn":"⛅ Погода","time_btn":"🕐 Время","loc_btn":"📍 Локация","help_btn":"❓ Помощь","back":"⬅️ Назад","choose_lang":"Выбери язык:","lang_saved":"✅ Язык сохранен: Русский",
"current_btn":"📍 Сейчас","today_btn":"📅 Сегодня","tomorrow_btn":"➡️ Завтра","week_btn":"📆 Неделя","hourly_btn":"⏰ По часам","rain_btn":"🌧 Дождь","wind_btn":"💨 Ветер","sun_btn":"🌅 Рассвет","uv_btn":"☀️ УФ-индекс","air_btn":"🌿 Воздух","alerts_btn":"⚠️ Тревоги",
"now_txt":"Сейчас в","feels_txt":"Ощущается как","humidity_txt":"Влажность","wind_txt":"Ветер","today_txt":"Сегодня","tomorrow_txt":"Завтра","week_txt":"Прогноз на 7 дней","rain_txt":"Дождь","sun_txt":"Солнце","rise_txt":"Рассвет","set_txt":"Закат"
},
"uk":{
"name":"🇺🇦 UA Українська",
"welcome":"Привіт! Я твій особистий метеоролог\n\nТисни ⛅ Погода внизу",
"weather_btn":"⛅ Погода","time_btn":"🕐 Час","loc_btn":"📍 Локація","help_btn":"❓ Допомога","back":"⬅️ Назад","choose_lang":"Обери мову:","lang_saved":"✅ Мову збережено: Українська",
"current_btn":"📍 Зараз","today_btn":"📅 Сьогодні","tomorrow_btn":"➡️ Завтра","week_btn":"📆 Тиждень","hourly_btn":"⏰ Погодинно","rain_btn":"🌧 Дощ","wind_btn":"💨 Вітер","sun_btn":"🌅 Сонце","uv_btn":"☀️ УФ","air_btn":"🌿 Повітря","alerts_btn":"⚠️ Тривоги",
"now_txt":"Зараз у","feels_txt":"Відчувається як","humidity_txt":"Вологість","wind_txt":"Вітер","today_txt":"Сьогодні","tomorrow_txt":"Завтра","week_txt":"7 днів","rain_txt":"Дощ","sun_txt":"Сонце","rise_txt":"Схід","set_txt":"Захід"
},
"be":{
"name":"🇧🇾 BY Беларуская",
"welcome":"Прывітанне! Я твой асабісты метэаролаг",
"weather_btn":"⛅ Надвор'е","time_btn":"🕐 Час","loc_btn":"📍 Лакацыя","help_btn":"❓ Дапамога","back":"⬅️ Назад","choose_lang":"Выберы мову:","lang_saved":"✅ Мова: Беларуская",
"current_btn":"📍 Зараз","today_btn":"📅 Сёння","tomorrow_btn":"➡️ Заўтра","week_btn":"📆 Тыдзень","hourly_btn":"⏰ Па гадзінах","rain_btn":"🌧 Дождж","wind_btn":"💨 Вецер","sun_btn":"🌅 Сонца","uv_btn":"☀️ УФ","air_btn":"🌿 Паветра","alerts_btn":"⚠️ Трывогі",
"now_txt":"Зараз у","feels_txt":"Адчуваецца як","humidity_txt":"Вільготнасць","wind_txt":"Вецер","today_txt":"Сёння","tomorrow_txt":"Заўтра","week_txt":"7 дзён","rain_txt":"Дождж","sun_txt":"Сонца","rise_txt":"Усход","set_txt":"Захад"
},
"sr":{
"name":"🇷🇸 RS Српски",
"welcome":"Здраво! Ја сам твој лични метеоролог\n\nТачније од iPhone-а\n\nПритисни ⛅ Време испод",
"weather_btn":"⛅ Време","time_btn":"🕐 Време и DST","loc_btn":"📍 Локација","help_btn":"❓ Помоћ","back":"⬅️ Назад","choose_lang":"Изабери језик:","lang_saved":"✅ Језик сачуван: Српски",
"current_btn":"📍 Тренутно","today_btn":"📅 Данас","tomorrow_btn":"➡️ Сутра","week_btn":"📆 Недеља","hourly_btn":"⏰ По сатима","rain_btn":"🌧 Киша","wind_btn":"💨 Ветар","sun_btn":"🌅 Сунце","uv_btn":"☀️ УВ","air_btn":"🌿 Ваздух","alerts_btn":"⚠️ Упозорења",
"now_txt":"Сада у","feels_txt":"Осећај","humidity_txt":"Влага","wind_txt":"Ветар","today_txt":"Данас","tomorrow_txt":"Сутра","week_txt":"7 дана","rain_txt":"Киша","sun_txt":"Сунце","rise_txt":"Излазак","set_txt":"Залазак"
},
"pl":{"name":"🇵🇱 PL Polski","welcome":"Cześć! Jestem twoim meteorologiem","weather_btn":"⛅ Pogoda","time_btn":"🕐 Czas","loc_btn":"📍 Lokalizacja","help_btn":"❓ Pomoc","back":"⬅️ Wróć","choose_lang":"Wybierz język:","lang_saved":"✅ Język: Polski","current_btn":"📍 Teraz","today_btn":"📅 Dziś","tomorrow_btn":"➡️ Jutro","week_btn":"📆 Tydzień","hourly_btn":"⏰ Co godzinę","rain_btn":"🌧 Deszcz","wind_btn":"💨 Wiatr","sun_btn":"🌅 Słońce","uv_btn":"☀️ UV","air_btn":"🌿 Powietrze","alerts_btn":"⚠️ Alerty","now_txt":"Teraz w","feels_txt":"Odczuwalna","humidity_txt":"Wilgotność","wind_txt":"Wiatr","today_txt":"Dziś","tomorrow_txt":"Jutro","week_txt":"7 dni","rain_txt":"Deszcz","sun_txt":"Słońce","rise_txt":"Wschód","set_txt":"Zachód"},
"de":{"name":"🇩🇪 DE Deutsch","welcome":"Hallo! Ich bin dein Meteorologe","weather_btn":"⛅ Wetter","time_btn":"🕐 Zeit","loc_btn":"📍 Standort","help_btn":"❓ Hilfe","back":"⬅️ Zurück","choose_lang":"Sprache wählen:","lang_saved":"✅ Sprache: Deutsch","current_btn":"📍 Jetzt","today_btn":"📅 Heute","tomorrow_btn":"➡️ Morgen","week_btn":"📆 Woche","hourly_btn":"⏰ Stündlich","rain_btn":"🌧 Regen","wind_btn":"💨 Wind","sun_btn":"🌅 Sonne","uv_btn":"☀️ UV","air_btn":"🌿 Luft","alerts_btn":"⚠️ Warnungen","now_txt":"Jetzt in","feels_txt":"Gefühlt","humidity_txt":"Feuchtigkeit","wind_txt":"Wind","today_txt":"Heute","tomorrow_txt":"Morgen","week_txt":"7 Tage","rain_txt":"Regen","sun_txt":"Sonne","rise_txt":"Sonnenaufgang","set_txt":"Sonnenuntergang"},
"fr":{"name":"🇫🇷 FR Français","welcome":"Salut! Je suis ton météorologue","weather_btn":"⛅ Météo","time_btn":"🕐 Heure","loc_btn":"📍 Lieu","help_btn":"❓ Aide","back":"⬅️ Retour","choose_lang":"Choisis langue:","lang_saved":"✅ Langue: Français","current_btn":"📍 Maintenant","today_btn":"📅 Aujourd'hui","tomorrow_btn":"➡️ Demain","week_btn":"📆 Semaine","hourly_btn":"⏰ Horaire","rain_btn":"🌧 Pluie","wind_btn":"💨 Vent","sun_btn":"🌅 Soleil","uv_btn":"☀️ UV","air_btn":"🌿 Air","alerts_btn":"⚠️ Alertes","now_txt":"Maintenant à","feels_txt":"Ressenti","humidity_txt":"Humidité","wind_txt":"Vent","today_txt":"Aujourd'hui","tomorrow_txt":"Demain","week_txt":"7 jours","rain_txt":"Pluie","sun_txt":"Soleil","rise_txt":"Lever","set_txt":"Coucher"},
"es":{"name":"🇪🇸 ES Español","welcome":"¡Hola! Soy tu meteorólogo","weather_btn":"⛅ Clima","time_btn":"🕐 Hora","loc_btn":"📍 Ubicación","help_btn":"❓ Ayuda","back":"⬅️ Atrás","choose_lang":"Elige idioma:","lang_saved":"✅ Idioma: Español","current_btn":"📍 Ahora","today_btn":"📅 Hoy","tomorrow_btn":"➡️ Mañana","week_btn":"📆 Semana","hourly_btn":"⏰ Por horas","rain_btn":"🌧 Lluvia","wind_btn":"💨 Viento","sun_btn":"🌅 Sol","uv_btn":"☀️ UV","air_btn":"🌿 Aire","alerts_btn":"⚠️ Alertas","now_txt":"Ahora en","feels_txt":"Sensación","humidity_txt":"Humedad","wind_txt":"Viento","today_txt":"Hoy","tomorrow_txt":"Mañana","week_txt":"7 días","rain_txt":"Lluvia","sun_txt":"Sol","rise_txt":"Amanecer","set_txt":"Atardecer"},
"it":{"name":"🇮🇹 IT Italiano","welcome":"Ciao! Sono il tuo meteorologo","weather_btn":"⛅ Meteo","time_btn":"🕐 Ora","loc_btn":"📍 Posizione","help_btn":"❓ Aiuto","back":"⬅️ Indietro","choose_lang":"Scegli lingua:","lang_saved":"✅ Lingua: Italiano","current_btn":"📍 Ora","today_btn":"📅 Oggi","tomorrow_btn":"➡️ Domani","week_btn":"📆 Settimana","hourly_btn":"⏰ Orario","rain_btn":"🌧 Pioggia","wind_btn":"💨 Vento","sun_btn":"🌅 Sole","uv_btn":"☀️ UV","air_btn":"🌿 Aria","alerts_btn":"⚠️ Allerte","now_txt":"Ora a","feels_txt":"Percepita","humidity_txt":"Umidità","wind_txt":"Vento","today_txt":"Oggi","tomorrow_txt":"Domani","week_txt":"7 giorni","rain_txt":"Pioggia","sun_txt":"Sole","rise_txt":"Alba","set_txt":"Tramonto"}
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
    k.row(tr(uid,"loc_btn"),"🌐 Language")
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
    k.row("🇷🇺 RU Русский","🇷🇸 RS Српски")
    k.row("🇺🇦 UA Українська","🇧🇾 BY Беларуская")
    k.row("🇬🇧 EN English","🇵🇱 PL Polski")
    k.row("🇩🇪 DE Deutsch","🇫🇷 FR Français")
    k.row("🇪🇸 ES Español","🇮🇹 IT Italiano")
    return k

def loc_kb(uid):
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.add(types.KeyboardButton("📍 Поделиться локацией",request_location=True))
    k.add(tr(uid,"back"))
    return k

@bot.message_handler(commands=["start","help"])
def start(m):
    uid=str(m.from_user.id)
    if uid not in U:
        bot.send_message(m.chat.id, "🌐 Choose your language / Выбери язык / Изабери језик:", reply_markup=lang_reply_kb())
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
    bot.send_message(m.chat.id,f"✅ Saved! {tz}",reply_markup=main_kb(uid))

@bot.message_handler(func=lambda m: m.text and any(x in m.text for x in ["EN English","RU Русский","RS Српски","UA Українська","BY Беларуская","PL Polski","DE Deutsch","FR Français","ES Español","IT Italiano"]))
def set_lang_text(m):
    txt=m.text
    code="en"
    if "RU Русский" in txt: code="ru"
    elif "RS Српски" in txt: code="sr"
    elif "UA Українська" in txt: code="uk"
    elif "BY Беларуская" in txt: code="be"
    elif "PL Polski" in txt: code="pl"
    elif "DE Deutsch" in txt: code="de"
    elif "FR Français" in txt: code="fr"
    elif "ES Español" in txt: code="es"
    elif "IT Italiano" in txt: code="it"
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
        bot.send_message(m.chat.id, f"lang={lang} data={U.get(s_uid)}")
        return
    if cmd=="location":
        bot.send_message(m.chat.id,"📍 Поделись локацией:",reply_markup=loc_kb(uid))
        return
    loc=get_user(uid)
    w=get_w(loc["lat"],loc["lon"])
    c=w["current"]; d=w["daily"]
    txt=""
    if cmd=="current":
        txt=f"{L['now_txt']} {loc['timezone']}\n\n🌡 {c['temperature_2m']}°C\n{L['feels_txt']}: {c['apparent_temperature']}°C\n{L['humidity_txt']}: {c['relative_humidity_2m']}%\n{L['wind_txt']}: {c['wind_speed_10m']} км/ч"
    elif cmd=="today":
        txt=f"{L['today_txt']} {d['time'][0]}\n\nМакс {d['temperature_2m_max'][0]}°C Мин {d['temperature_2m_min'][0]}°C\n{L['rain_txt']}: {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}мм"
    elif cmd=="tomorrow":
        txt=f"{L['tomorrow_txt']} {d['time'][1]}\n\nМакс {d['temperature_2m_max'][1]}°C Мин {d['temperature_2m_min'][1]}°C"
    elif cmd=="week":
        txt=f"{L['week_txt']}\n\n"
        for i in range(7):
            txt+=f"{d['time'][i]} {d['temperature_2m_min'][i]}°/{d['temperature_2m_max'][i]}° {d['precipitation_probability_max'][i]}%\n"
    elif cmd=="hourly":
        h=w["hourly"]; txt=f"{L['hourly_btn']}\n\n"
        for i in range(12):
            txt+=f"{h['time'][i][11:]} {h['temperature_2m'][i]}°C {h['precipitation_probability'][i]}%\n"
    elif cmd=="rain":
        txt=f"{L['rain_txt']} {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}мм"
    elif cmd=="wind":
        txt=f"{L['wind_txt']} {c['wind_speed_10m']} км/ч Макс {d['wind_speed_10m_max'][0]}"
    elif cmd=="sun":
        txt=f"{L['sun_txt']}\n{L['rise_txt']}: {d['sunrise'][0][11:]}\n{L['set_txt']}: {d['sunset'][0][11:]}"
    elif cmd=="uv":
        txt=f"UV {d['uv_index_max'][0]}"
    elif cmd=="air":
        txt="🌿 Воздух - данные скоро"
    elif cmd=="alerts":
        txt="⚠️ Нет предупреждений"
    elif cmd=="time":
        now=datetime.now(ZoneInfo(loc["timezone"]))
        txt=f"🕐 {now.strftime('%H:%M:%S %d %B')} {loc['timezone']}"
    elif cmd=="dst":
        txt=get_dst_info(loc["timezone"])
    elif cmd=="mylocation":
        txt=f"{loc['lat']},{loc['lon']}"
    kb=weather_kb(uid) if cmd in ["current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts"] else main_kb(uid)
    bot.send_message(m.chat.id,txt,reply_markup=kb)

def get_dst_info(tz_name):
    try:
        z=ZoneInfo(tz_name)
        n=datetime.now(z)
        return f"{tz_name} {n.strftime('%H:%M %d %B')}"
    except:
        return tz_name

@bot.message_handler(func=lambda m:True)
def buttons(m):
    uid=m.from_user.id
    s_uid=str(uid)
    lang=U.get(s_uid,{}).get("lang","en")
    mapping=get_all_btns(lang)
    t=(m.text or "").strip()
    for btn_text, action in mapping.items():
        if t==btn_text:
            if action=="back":
                bot.send_message(m.chat.id,"Меню",reply_markup=main_kb(uid)); return
            elif action=="weather":
                bot.send_message(m.chat.id,"⛅ Погода:",reply_markup=weather_kb(uid)); return
            elif action=="dst":
                m.text="/dst"; return profi(m)
            elif action=="location":
                m.text="/location"; return profi(m)
            elif action=="help":
                return start(m)
            else:
                m.text=f"/{action}"; return profi(m)
    if "Language" in t or "🌐" in t:
        bot.send_message(m.chat.id,tr(uid,"choose_lang"),reply_markup=lang_reply_kb()); return
    bot.send_message(m.chat.id,"Меню",reply_markup=main_kb(uid))

app=Flask(__name__)
@app.route("/")
def home():
    return "CYRILLIC OK"

def run_web():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_web,daemon=True).start()
while True:
    try:
        bot.infinity_polling(skip_pending=False,timeout=60)
    except Exception as e:
        print(e); time.sleep(5)
