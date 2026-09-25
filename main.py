from flask import Flask
import threading, telebot, requests, json, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot import types
from dotenv import load_dotenv
load_dotenv()

TOKEN=os.getenv("TOKEN")
WAPI_KEY=os.getenv("WEATHERAPI_KEY") # <-- добавь на Render
bot=telebot.TeleBot(TOKEN)
bot.remove_webhook()

FILE="locations.json"
U={}
if os.path.exists(FILE):
    try:
        U=json.load(open(FILE,"r",encoding="utf-8"))
    except:
        U={}
def save():
    json.dump(U,open(FILE,"w",encoding="utf-8"),ensure_ascii=False)

# КЭШ 10 минут - чтобы не улетать в лимиты
CACHE={}
CACHE_TTL=600

WELCOME_RU="""👋 Привет! Я твой персональный метеоролог

Я покажу погоду точнее чем iPhone, и никогда не забуду про перевод часов.

📍 ЧТО Я УМЕЮ:

🌤 ПОГОДА:
- /current — сейчас: температура, ощущается, влажность
- /today — подробно на сегодня
- /tomorrow — прогноз на завтра
- /week — 7 дней вперед
- /hourly — по часам на 24ч

🔍 ДЕТАЛИ:
- /rain — дождь: вероятность + мм
- /wind — ветер + порывы в м/с
- /sun — рассвет, закат, долгота дня
- /uv — UV индекс + совет
- /air — качество воздуха AQI
- /alerts — предупреждения

⏰ ВРЕМЯ:
- /time — точное время у тебя
- /dst — летнее/зимнее + когда перевод

📍 ЛОКАЦИЯ:
- /location — сменить город
- /mylocation — где я сейчас

Нажми Share Location чтобы начать.
Данные: Open-Meteo + WeatherAPI • Работаю 24/7"""

WELCOME_EN="""👋 Hi! I'm your personal meteorologist

I show weather more accurate than iPhone, and I never forget DST.

📍 WHAT I CAN DO:

🌤 WEATHER:
- /current — now: temp, feels like, humidity
- /today — detailed today
- /tomorrow — tomorrow forecast
- /week — 7 days ahead
- /hourly — hourly 24h

🔍 DETAILS:
- /rain — rain: chance + mm
- /wind — wind + gusts in m/s
- /sun — sunrise, sunset, day length
- /uv — UV index + advice
- /air — air quality AQI
- /alerts — warnings

⏰ TIME:
- /time — your exact time
- /dst — summer/winter + DST change

📍 LOCATION:
- /location — change city
- /mylocation — where I am

Press Share Location to start.
Data: Open-Meteo + WeatherAPI • Working 24/7"""

WELCOME_SR="""👋 Здраво! Ја сам твој лични метеоролог

Показујем време тачније од iPhone-а и никад не заборављам летње/зимско рачунање.

📍 ШТА УМЕМ:

🌤 ВРЕМЕ:
- /current — сада: температура, осећај, влажност
- /today — детаљно за данас
- /tomorrow — прогноза за сутра
- /week — 7 дана унапред
- /hourly — по сатима 24ч

🔍 ДЕТАЉИ:
- /rain — киша: вероватноћа + мм
- /wind — ветар + удари у м/с
- /sun — излазак, залазак, дужина дана
- /uv — УВ индекс + савет
- /air — квалитет ваздуха AQI
- /alerts — упозорења

⏰ ВРЕМЕ:
- /time — тачно време код тебе
- /dst — летње/зимско + када је промена"""

WELCOME_UK="""👋 Привіт! Я твій персональний метеоролог

Покажу погоду точніше за iPhone і ніколи не забуду про переведення годинника.

📍 ЩО ВМІЮ:

🌤 ПОГОДА:
- /current — зараз: температура, відчувається, вологість
- /today — детально на сьогодні
- /tomorrow — прогноз на завтра
- /week — 7 днів вперед
- /hourly — по годинах 24г

🔍 ДЕТАЛІ:
- /rain — дощ: ймовірність + мм
- /wind — вітер + пориви у м/с
- /sun — схід, захід, довгота дня
- /uv — УФ індекс + порада
- /air — якість повітря AQI
- /alerts — попередження"""

WELCOME_BE="""👋 Прывітанне! Я твой персанальны метэаролаг

Пакажу надвор'е дакладней чым iPhone і ніколі не забуду пра перавод гадзінніка.

📍 ШТО ЎМЕЮ:

🌤 НАДВОР'Е:
- /current — зараз: тэмпература, адчуваецца, вільготнасць
- /today — падрабязна на сёння
- /tomorrow — прагноз на заўтра
- /week — 7 дзён наперад
- /hourly — па гадзінах 24г

🔍 ДЭТАЛІ:
- /rain — дождж: імавернасць + мм
- /wind — вецер + павевы ў м/с
- /sun — усход, захад, даўжыня дня
- /uv — УФ індэкс + парада"""

WELCOME_PL="""👋 Cześć! Jestem Twoim osobistym meteorologiem

Pokazuję pogodę dokładniej niż iPhone i nigdy nie zapomnę o zmianie czasu.

📍 CO POTRAFIĘ:

🌤 POGODA:
- /current — teraz: temperatura, odczuwalna, wilgotność
- /today — szczegółowo dziś
- /tomorrow — prognoza na jutro
- /week — 7 dni naprzód
- /hourly — co godzinę 24h

🔍 SZCZEGÓŁY:
- /rain — deszcz: prawdopodobieństwo + mm
- /wind — wiatr + porywy w m/s
- /sun — wschód, zachód, długość dnia
- /uv — indeks UV + porada"""

WELCOME_DE="""👋 Hallo! Ich bin dein persönlicher Meteorologe

Ich zeige Wetter genauer als iPhone und vergesse nie die Zeitumstellung.

📍 WAS ICH KANN:

🌤 WETTER:
- /current — jetzt: Temperatur, gefühlt, Feuchtigkeit
- /today — detailliert heute
- /tomorrow — Prognose morgen
- /week — 7 Tage voraus
- /hourly — stündlich 24h

🔍 DETAILS:
- /rain — Regen: Wahrscheinlichkeit + mm
- /wind — Wind + Böen in m/s
- /sun — Aufgang, Untergang, Tageslänge
- /uv — UV-Index + Tipp"""

WELCOME_FR="""👋 Salut! Je suis ton météorologue personnel

Plus précis qu'iPhone, je n'oublie jamais le changement d'heure.

📍 CE QUE JE FAIS:

🌤 MÉTÉO:
- /current — maintenant: température, ressenti, humidité
- /today — détaillé aujourd'hui
- /tomorrow — prévision demain
- /week — 7 jours à venir
- /hourly — horaire 24h

🔍 DÉTAILS:
- /rain — pluie: probabilité + mm
- /wind — vent + rafales en m/s
- /sun — lever, coucher, durée du jour
- /uv — indice UV + conseil"""

WELCOME_ES="""👋 Hola! Soy tu meteorólogo personal

Más preciso que iPhone, nunca olvido el cambio de hora.

📍 QUÉ HAGO:

🌤 CLIMA:
- /current — ahora: temperatura, sensación, humedad
- /today — detallado hoy
- /tomorrow — pronóstico mañana
- /week — 7 días adelante
- /hourly — por horas 24h

🔍 DETALLES:
- /rain — lluvia: probabilidad + mm
- /wind — viento + ráfagas en m/s
- /sun — amanecer, atardecer, duración día
- /uv — índice UV + consejo"""

WELCOME_IT="""👋 Ciao! Sono il tuo meteorologo personale

Più preciso di iPhone, non dimentico mai l'ora legale.

📍 COSA SO FARE:

🌤 METEO:
- /current — ora: temperatura, percepita, umidità
- /today — dettagliato oggi
- /tomorrow — previsione domani
- /week — 7 giorni avanti
- /hourly — orario 24h

🔍 DETTAGLI:
- /rain — pioggia: probabilità + mm
- /wind — vento + raffiche in m/s
- /sun — alba, tramonto, durata giorno
- /uv — indice UV + consiglio"""

LANGS={
"ru":{"welcome":WELCOME_RU,"weather_btn":"🌤 Погода","time_btn":"🕐 Время","loc_btn":"📍 Локация","help_btn":"❓ Помощь","back":"⬅️ Назад","choose_lang":"🌐 Выбери язык:","lang_saved":"✅ Русский","current_btn":"📍 Сейчас","today_btn":"📅 Сегодня","tomorrow_btn":"➡️ Завтра","week_btn":"📆 Неделя","hourly_btn":"⏰ По часам","rain_btn":"🌧 Дождь","wind_btn":"💨 Ветер","sun_btn":"🌅 Солнце","uv_btn":"☀️ УФ","air_btn":"🌿 Воздух","alerts_btn":"⚠️ Тревоги","now_txt":"Сейчас в","feels_txt":"Ощущается","humidity_txt":"Влажность","wind_txt":"Ветер","today_txt":"Сегодня","tomorrow_txt":"Завтра","week_txt":"7 дней","rain_txt":"Дождь","rise_txt":"Рассвет","set_txt":"Закат"},
"en":{"welcome":WELCOME_EN,"weather_btn":"🌤 Whether commands","time_btn":"🕐 Time","loc_btn":"📍 Location","help_btn":"❓ Help","back":"⬅️ Back","choose_lang":"🌐 Choose language:","lang_saved":"✅ English","current_btn":"📍 Current","today_btn":"📅 Today","tomorrow_btn":"➡️ Tomorrow","week_btn":"📆 Week","hourly_btn":"⏰ Hourly","rain_btn":"🌧 Rain","wind_btn":"💨 Wind","sun_btn":"🌅 Sun","uv_btn":"☀️ UV","air_btn":"🌿 Air","alerts_btn":"⚠️ Alerts","now_txt":"Now in","feels_txt":"Feels","humidity_txt":"Humidity","wind_txt":"Wind","today_txt":"Today","tomorrow_txt":"Tomorrow","week_txt":"7 days","rain_txt":"Rain","rise_txt":"Sunrise","set_txt":"Sunset"},
"sr":{"welcome":WELCOME_SR,"weather_btn":"🌤 Време","time_btn":"🕐 Време","loc_btn":"📍 Локација","help_btn":"❓ Помоћ","back":"⬅️ Назад","choose_lang":"🌐 Језик:","lang_saved":"✅ Српски","current_btn":"📍 Тренутно","today_btn":"📅 Данас","tomorrow_btn":"➡️ Сутра","week_btn":"📆 Недеља","hourly_btn":"⏰ По сатима","rain_btn":"🌧 Киша","wind_btn":"💨 Ветар","sun_btn":"🌅 Сунце","uv_btn":"☀️ УВ","air_btn":"🌿 Ваздух","alerts_btn":"⚠️ Упозорења","now_txt":"Сада у","feels_txt":"Осећај","humidity_txt":"Влага","wind_txt":"Ветар","today_txt":"Данас","tomorrow_txt":"Сутра","week_txt":"7 дана","rain_txt":"Киша","rise_txt":"Излазак","set_txt":"Залазак"},
"uk":{"welcome":WELCOME_UK,"weather_btn":"🌤 Погода","time_btn":"🕐 Час","loc_btn":"📍 Локація","help_btn":"❓ Допомога","back":"⬅️ Назад","choose_lang":"🌐 Мова:","lang_saved":"✅ Українська","current_btn":"📍 Зараз","today_btn":"📅 Сьогодні","tomorrow_btn":"➡️ Завтра","week_btn":"📆 Тиждень","hourly_btn":"⏰ Погодинно","rain_btn":"🌧 Дощ","wind_btn":"💨 Вітер","sun_btn":"🌅 Сонце","uv_btn":"☀️ УФ","air_btn":"🌿 Повітря","alerts_btn":"⚠️ Тривоги","now_txt":"Зараз у","feels_txt":"Відчувається","humidity_txt":"Вологість","wind_txt":"Вітер","today_txt":"Сьогодні","tomorrow_txt":"Завтра","week_txt":"7 днів","rain_txt":"Дощ","rise_txt":"Схід","set_txt":"Захід"},
"be":{"welcome":WELCOME_BE,"weather_btn":"🌤 Надвор'е","time_btn":"🕐 Час","loc_btn":"📍 Лакацыя","help_btn":"❓ Дапамога","back":"⬅️ Назад","choose_lang":"🌐 Мова:","lang_saved":"✅ Беларуская","current_btn":"📍 Зараз","today_btn":"📅 Сёння","tomorrow_btn":"➡️ Заўтра","week_btn":"📆 Тыдзень","hourly_btn":"⏰ Па гадзінах","rain_btn":"🌧 Дождж","wind_btn":"💨 Вецер","sun_btn":"🌅 Сонца","uv_btn":"☀️ УФ","air_btn":"🌿 Паветра","alerts_btn":"⚠️ Трывогі","now_txt":"Зараз у","feels_txt":"Адчуваецца","humidity_txt":"Вільготнасць","wind_txt":"Вецер","today_txt":"Сёння","tomorrow_txt":"Заўтра","week_txt":"7 дзён","rain_txt":"Дождж","rise_txt":"Усход","set_txt":"Захад"},
"pl":{"welcome":WELCOME_PL,"weather_btn":"🌤 Pogoda","time_btn":"🕐 Czas","loc_btn":"📍 Lokalizacja","help_btn":"❓ Pomoc","back":"⬅️ Wróć","choose_lang":"🌐 Język:","lang_saved":"✅ Polski","current_btn":"📍 Teraz","today_btn":"📅 Dziś","tomorrow_btn":"➡️ Jutro","week_btn":"📆 Tydzień","hourly_btn":"⏰ Co godzinę","rain_btn":"🌧 Deszcz","wind_btn":"💨 Wiatr","sun_btn":"🌅 Słońce","uv_btn":"☀️ UV","air_btn":"🌿 Powietrze","alerts_btn":"⚠️ Alerty","now_txt":"Teraz w","feels_txt":"Odczuwalna","humidity_txt":"Wilgotność","wind_txt":"Wiatr","today_txt":"Dziś","tomorrow_txt":"Jutro","week_txt":"7 dni","rain_txt":"Deszcz","rise_txt":"Wschód","set_txt":"Zachód"},
"de":{"welcome":WELCOME_DE,"weather_btn":"🌤 Wetter","time_btn":"🕐 Zeit","loc_btn":"📍 Standort","help_btn":"❓ Hilfe","back":"⬅️ Zurück","choose_lang":"🌐 Sprache:","lang_saved":"✅ Deutsch","current_btn":"📍 Jetzt","today_btn":"📅 Heute","tomorrow_btn":"➡️ Morgen","week_btn":"📆 Woche","hourly_btn":"⏰ Stündlich","rain_btn":"🌧 Regen","wind_btn":"💨 Wind","sun_btn":"🌅 Sonne","uv_btn":"☀️ UV","air_btn":"🌿 Luft","alerts_btn":"⚠️ Warnungen","now_txt":"Jetzt in","feels_txt":"Gefühlt","humidity_txt":"Feuchtigkeit","wind_txt":"Wind","today_txt":"Heute","tomorrow_txt":"Morgen","week_txt":"7 Tage","rain_txt":"Regen","rise_txt":"Aufgang","set_txt":"Untergang"},
"fr":{"welcome":WELCOME_FR,"weather_btn":"🌤 Météo","time_btn":"🕐 Heure","loc_btn":"📍 Lieu","help_btn":"❓ Aide","back":"⬅️ Retour","choose_lang":"🌐 Langue:","lang_saved":"✅ Français","current_btn":"📍 Maintenant","today_btn":"📅 Aujourd'hui","tomorrow_btn":"➡️ Demain","week_btn":"📆 Semaine","hourly_btn":"⏰ Horaire","rain_btn":"🌧 Pluie","wind_btn":"💨 Vent","sun_btn":"🌅 Soleil","uv_btn":"☀️ UV","air_btn":"🌿 Air","alerts_btn":"⚠️ Alertes","now_txt":"Maintenant à","feels_txt":"Ressenti","humidity_txt":"Humidité","wind_txt":"Vent","today_txt":"Aujourd'hui","tomorrow_txt":"Demain","week_txt":"7 jours","rain_txt":"Pluie","rise_txt":"Lever","set_txt":"Coucher"},
"es":{"welcome":WELCOME_ES,"weather_btn":"🌤 Clima","time_btn":"🕐 Hora","loc_btn":"📍 Ubicación","help_btn":"❓ Ayuda","back":"⬅️ Atrás","choose_lang":"🌐 Idioma:","lang_saved":"✅ Español","current_btn":"📍 Ahora","today_btn":"📅 Hoy","tomorrow_btn":"➡️ Mañana","week_btn":"📆 Semana","hourly_btn":"⏰ Por horas","rain_btn":"🌧 Lluvia","wind_btn":"💨 Viento","sun_btn":"🌅 Sol","uv_btn":"☀️ UV","air_btn":"🌿 Aire","alerts_btn":"⚠️ Alertas","now_txt":"Ahora en","feels_txt":"Sensación","humidity_txt":"Humedad","wind_txt":"Viento","today_txt":"Hoy","tomorrow_txt":"Mañana","week_txt":"7 días","rain_txt":"Lluvia","rise_txt":"Amanecer","set_txt":"Atardecer"},
"it":{"welcome":WELCOME_IT,"weather_btn":"🌤 Meteo","time_btn":"🕐 Ora","loc_btn":"📍 Posizione","help_btn":"❓ Aiuto","back":"⬅️ Indietro","choose_lang":"🌐 Lingua:","lang_saved":"✅ Italiano","current_btn":"📍 Ora","today_btn":"📅 Oggi","tomorrow_btn":"➡️ Domani","week_btn":"📆 Settimana","hourly_btn":"⏰ Orario","rain_btn":"🌧 Pioggia","wind_btn":"💨 Vento","sun_btn":"🌅 Sole","uv_btn":"☀️ UV","air_btn":"🌿 Aria","alerts_btn":"⚠️ Allerte","now_txt":"Ora a","feels_txt":"Percepita","humidity_txt":"Umidità","wind_txt":"Vento","today_txt":"Oggi","tomorrow_txt":"Domani","week_txt":"7 giorni","rain_txt":"Pioggia","rise_txt":"Alba","set_txt":"Tramonto"}
}

def get_user(uid):
    info=U.get(str(uid), {"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade","lang":"ru"})
    if info.get("lang") not in LANGS: info["lang"]="ru"
    return info
def tr(uid,key):
    lang=get_user(uid).get("lang","ru")
    return LANGS.get(lang, LANGS["ru"]).get(key,key)

# ===== 1. OPEN-METEO =====
def fetch_openmeteo(lat,lon):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7&wind_speed_unit=ms"
    r=requests.get(url,timeout=12).json()
    if "current" in r:
        r["_source"]="open-meteo"
        return r
    print("OPEN-METEO FAIL:", r)
    return None

# ===== 2. WEATHERAPI =====
def fetch_weatherapi(lat,lon):
    if not WAPI_KEY:
        print("NO WAPI_KEY")
        return None
    try:
        url=f"https://api.weatherapi.com/v1/forecast.json?key={WAPI_KEY}&q={lat},{lon}&days=7&aqi=yes&alerts=yes"
        j=requests.get(url,timeout=12).json()
        if "error" in j:
            print("WEATHERAPI ERROR:", j)
            return None
        # конвертим в формат open-meteo чтобы не переписывать весь код
        cur=j["current"]
        fore=j["forecast"]["forecastday"]
        daily={
            "time":[d["date"] for d in fore],
            "temperature_2m_max":[d["day"]["maxtemp_c"] for d in fore],
            "temperature_2m_min":[d["day"]["mintemp_c"] for d in fore],
            "precipitation_probability_max":[d["day"]["daily_chance_of_rain"] for d in fore],
            "precipitation_sum":[d["day"]["totalprecip_mm"] for d in fore],
            "sunrise":[d["astro"]["sunrise"] for d in fore],
            "sunset":[d["astro"]["sunset"] for d in fore],
            "uv_index_max":[d["day"]["uv"] for d in fore],
            "wind_speed_10m_max":[round(d["day"]["maxwind_kph"]/3.6,1) for d in fore],
            "wind_gusts_10m_max":[round(d["day"]["maxwind_kph"]/3.6,1) for d in fore],
        }
        # hourly - берем первые 24 часа из сегодня
        hourly_times=[]
        hourly_temp=[]
        hourly_prec=[]
        for h in fore[0]["hour"]:
            hourly_times.append(h["time"])
            hourly_temp.append(h["temp_c"])
            hourly_prec.append(h["chance_of_rain"])
        converted={
            "current":{
                "temperature_2m":cur["temp_c"],
                "apparent_temperature":cur["feelslike_c"],
                "relative_humidity_2m":cur["humidity"],
                "wind_speed_10m":round(cur["wind_kph"]/3.6,1) # в м/с
            },
            "daily":daily,
            "hourly":{
                "time":hourly_times,
                "temperature_2m":hourly_temp,
                "precipitation_probability":hourly_prec
            },
            "timezone":j["location"]["tz_id"],
            "_source":"weatherapi"
        }
        return converted
    except Exception as e:
        print("WAPI EXC:", e)
        return None

# ===== ГИБРИД С ФОЛБЭКОМ =====
def get_w(lat,lon):
    key=f"{round(lat,2)}_{round(lon,2)}"
    now_ts=time.time()
    if key in CACHE and now_ts - CACHE[key][0] < CACHE_TTL:
        return CACHE[key][1]

    # пробуем open-meteo первым
    data=fetch_openmeteo(lat,lon)
    if data:
        CACHE[key]=(now_ts,data)
        return data

    print("Open-Meteo limit - переключаюсь на WeatherAPI")
    data=fetch_weatherapi(lat,lon)
    if data:
        CACHE[key]=(now_ts,data)
        return data

    # если и weatherapi упал - пробуем еще раз open-meteo без ms (на случай глюка)
    print("WeatherAPI тоже упал - пробую снова Open-Meteo без ms")
    try:
        url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max&hourly=temperature_2m,precipitation_probability&timezone=auto&forecast_days=7"
        r=requests.get(url,timeout=12).json()
        if "current" in r:
            r["_source"]="open-meteo-fallback"
            CACHE[key]=(now_ts,r)
            return r
    except:
        pass
    return {"error":True,"reason":"both apis failed"}

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
def lang_kb():
    k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    k.row("RU Русский","RS Српски","EN English")
    k.row("UA Українська","BY Беларуская","PL Polski")
    k.row("DE Deutsch","FR Français","ES Español","IT Italiano")
    return k

def do_cmd(chat_id, uid, cmd):
    try:
        s_uid=str(uid)
        if s_uid not in U and cmd=="start":
            bot.send_message(chat_id, "🌐 Выбери язык / Choose language / Изабери језик:", reply_markup=lang_kb())
            return
        if cmd=="start":
            L=LANGS.get(get_user(uid).get("lang","ru"), LANGS["ru"])
            bot.send_message(chat_id, L["welcome"], reply_markup=main_kb(uid))
            return
        if cmd=="language":
            bot.send_message(chat_id, tr(uid,"choose_lang"), reply_markup=lang_kb())
            return
        if cmd=="location":
            k=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            k.add(types.KeyboardButton("📍 Поделиться локацией",request_location=True))
            k.add(tr(uid,"back"))
            bot.send_message(chat_id, "📍 Поделись локацией:", reply_markup=k)
            return

        loc=get_user(uid)
        w=get_w(loc["lat"],loc["lon"])
        if not w or "current" not in w:
            bot.send_message(chat_id, "⏳ Оба сервиса заняты, подожди минуту. Кэш уже включен чтобы не банило.")
            return

        c=w["current"]; d=w["daily"]
        L=LANGS.get(get_user(uid).get("lang","ru"), LANGS["ru"])
        src=w.get("_source","")
        src_icon="☁️" if "weatherapi" in src else "🌐"

        txt=""
        if cmd=="current": txt=f"{src_icon} {L['now_txt']} {loc['timezone']}\n\n🌡 {c['temperature_2m']}°C\n{L['feels_txt']}: {c['apparent_temperature']}°C\n{L['humidity_txt']}: {c['relative_humidity_2m']}%\n{L['wind_txt']}: {c['wind_speed_10m']} м/с"
        elif cmd=="today": txt=f"📅 {L['today_txt']} {d['time'][0]} {d['temperature_2m_max'][0]}/{d['temperature_2m_min'][0]}°C {L['rain_txt']} {d['precipitation_probability_max'][0]}%"
        elif cmd=="tomorrow": txt=f"➡️ {L['tomorrow_txt']} {d['time'][1]} {d['temperature_2m_max'][1]}/{d['temperature_2m_min'][1]}°C"
        elif cmd=="week":
            txt=f"📆 {L['week_txt']}\n"
            for i in range(min(7,len(d['time']))): txt+=f"{d['time'][i]} {d['temperature_2m_min'][i]}/{d['temperature_2m_max'][i]}°C {d['precipitation_probability_max'][i]}%\n"
        elif cmd=="hourly":
            h=w["hourly"]; txt="⏰\n"
            for i in range(min(12,len(h['time']))):
                t=h['time'][i]
                if " " in t: t=t.split()[1]
                else: t=t[11:] if len(t)>11 else t
                txt+=f"{t} {h['temperature_2m'][i]}°C {h['precipitation_probability'][i]}%\n"
        elif cmd=="rain": txt=f"🌧 {L['rain_txt']} {d['precipitation_probability_max'][0]}% {d['precipitation_sum'][0]}мм"
        elif cmd=="wind": txt=f"💨 {L['wind_txt']}: {c['wind_speed_10m']} м/с\nПорывы: {d['wind_gusts_10m_max'][0]} м/с"
        elif cmd=="sun": txt=f"🌅 {L['rise_txt']}: {d['sunrise'][0]}\n🌇 {L['set_txt']}: {d['sunset'][0]}"
        elif cmd=="uv": txt=f"☀️ UV {d['uv_index_max'][0]}"
        elif cmd=="air": txt="🌿 Воздух — скоро"
        elif cmd=="alerts": txt="⚠️ Нет тревог"
        elif cmd in ["time","dst"]:
            now=datetime.now(ZoneInfo(loc["timezone"]))
            txt=f"🕐 {now.strftime('%H:%M:%S %d.%m.%Y')} {loc['timezone']}"
        elif cmd=="mylocation": txt=f"{loc['lat']},{loc['lon']} {loc['timezone']}"
        bot.send_message(chat_id, txt, reply_markup=weather_kb(uid))
    except Exception as e:
        import traceback; traceback.print_exc()
        bot.send_message(chat_id, f"Ошибка {cmd}: {e}")

@bot.message_handler(commands=["start","current","today","tomorrow","week","hourly","rain","wind","sun","uv","air","alerts","time","dst","location","mylocation","language","lang","help"])
def all_commands(m):
    cmd=m.text.split()[0].lstrip("/").split("@")[0].lower()
    if cmd=="lang": cmd="language"
    if cmd=="help": cmd="start"
    do_cmd(m.chat.id, m.from_user.id, cmd)

@bot.message_handler(content_types=["location"])
def loc_h(m):
    # не дергаем API при получении локации - просто сохраняем, кэш сам обновится при первой команде
    uid=str(m.from_user.id)
    # пытаемся узнать таймзону без тяжелого запроса
    try:
        w=fetch_openmeteo(m.location.latitude,m.location.longitude)
        tz=w.get("timezone","Europe/Belgrade") if w else "Europe/Belgrade"
    except:
        tz="Europe/Belgrade"
    cur=get_user(m.from_user.id)
    cur.update({"lat":m.location.latitude,"lon":m.location.longitude,"timezone":tz})
    U[uid]=cur
    save()
    bot.send_message(m.chat.id,f"✅ {tz} 📍",reply_markup=main_kb(m.from_user.id))

@bot.message_handler(func=lambda m: m.text in ["RU Русский","RS Српски","EN English","UA Українська","BY Беларуская","PL Polski","DE Deutsch","FR Français","ES Español","IT Italiano"])
def lang_h(m):
    mp={"RU Русский":"ru","RS Српски":"sr","EN English":"en","UA Українська":"uk","BY Беларуская":"be","PL Polski":"pl","DE Deutsch":"de","FR Français":"fr","ES Español":"es","IT Italiano":"it"}
    code=mp[m.text]
    uid=str(m.from_user.id)
    if uid not in U:
        U[uid]={"lat":44.81,"lon":20.46,"timezone":"Europe/Belgrade","lang":code}
    else:
        U[uid]["lang"]=code
    save()
    bot.send_message(m.chat.id, LANGS[code]["lang_saved"], reply_markup=main_kb(m.from_user.id))
    bot.send_message(m.chat.id, LANGS[code]["welcome"], reply_markup=main_kb(m.from_user.id))

@bot.message_handler(func=lambda m: True)
def btn_h(m):
    uid=m.from_user.id
    t=(m.text or "").strip()
    for L in LANGS.values():
        if t==L["weather_btn"]:
            bot.send_message(m.chat.id, "🌤", reply_markup=weather_kb(uid)); return
        if t==L["time_btn"]:
            do_cmd(m.chat.id, uid, "dst"); return
        if t==L["loc_btn"]:
            do_cmd(m.chat.id, uid, "location"); return
        if t==L["help_btn"]:
            do_cmd(m.chat.id, uid, "start"); return
        if t==L["back"]:
            bot.send_message(m.chat.id, "Меню", reply_markup=main_kb(uid)); return
        for k in ["current_btn","today_btn","tomorrow_btn","week_btn","hourly_btn","rain_btn","wind_btn","sun_btn","uv_btn","air_btn","alerts_btn"]:
            if t==L[k]:
                do_cmd(m.chat.id, uid, k.replace("_btn","")); return
    if "Language" in t or "язык" in t.lower() or "језик" in t.lower():
        do_cmd(m.chat.id, uid, "language"); return

app=Flask(__name__)
@app.route("/")
def home():
    return "HYBRID OPEN-METEO + WEATHERAPI + CACHE + ALL WELCOMES"
def run_web():
    app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_web,daemon=True).start()
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=10)
    except Exception as e:
        print("POLL ERR", e)
        time.sleep(3)
