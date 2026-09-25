ALL_LANGUAGES = {
    "en": {
        "greeting": """👋 Hi! I'm your personal meteorologist

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
Data: Open-Meteo + WeatherAPI • Working 24/7""",
        "time": "⏰ Your local time: {time}\n📍 {city}\n🌍 Timezone: {tz}",
        "dst": "⏰ DST for {city}\nCurrent: {is_dst} ({dst_status})\nTimezone: {tz}\nNext: {next_change}\nIn {days} days clocks go {direction} by 1 hour.",
        "buttons": {"share": "📍 Share Location", "time": "⏰ Time", "dst": "⏰ DST", "today": "🌤 Today", "week": "📅 Week"}
    },
    "ru": {
        "greeting": """👋 Привет! Я твой личный метеоролог

Показываю погоду точнее чем iPhone и никогда не забываю про перевод часов.

📍 ЧТО Я УМЕЮ:

🌤 ПОГОДА:
- /current — сейчас: темп, ощущается, влажность
- /today — подробно на сегодня
- /tomorrow — прогноз на завтра
- /week — на 7 дней вперед
- /hourly — по часам на 24ч

🔍 ДЕТАЛИ:
- /rain — дождь: шанс + мм
- /wind — ветер + порывы в м/с
- /sun — восход, закат, долгота дня
- /uv — УФ индекс + советы
- /air — качество воздуха AQI
- /alerts — предупреждения

⏰ ВРЕМЯ:
- /time — твое точное время
- /dst — лето/зима + перевод часов

📍 ЛОКАЦИЯ:
- /location — сменить город
- /mylocation — где я нахожусь

Нажми Поделиться локацией чтобы начать.
Данные: Open-Meteo + WeatherAPI • Работаю 24/7""",
        "time": "⏰ Твое местное время: {time}\n📍 {city}\n🌍 Часовой пояс: {tz}",
        "dst": "⏰ Перевод часов для {city}\nСейчас: {is_dst}\nСледующий: {next_change}\nЧерез {days} дней часы {direction} на 1 час.",
        "buttons": {"share": "📍 Поделиться локацией", "time": "⏰ Время", "dst": "⏰ Перевод часов", "today": "🌤 Сегодня", "week": "📅 Неделя"}
    },
    "fr": {
        "greeting": """👋 Salut! Je suis ton météorologue personnel

Je montre la météo plus précise que l'iPhone et je n'oublie jamais le changement d'heure.

📍 CE QUE JE SAIS FAIRE:

🌤 MÉTÉO:
- /current — maintenant: temp, ressenti, humidité
- /today — détaillé aujourd'hui
- /tomorrow — prévision demain
- /week — 7 jours à venir
- /hourly — heure par heure 24h

🔍 DÉTAILS:
- /rain — pluie: chance + mm
- /wind — vent + rafales en m/s
- /sun — lever, coucher, durée du jour
- /uv — indice UV + conseils
- /air — qualité de l'air AQI
- /alerts — alertes

⏰ HEURE:
- /time — ton heure exacte
- /dst — été/hiver + changement d'heure

📍 LOCALISATION:
- /location — changer de ville
- /mylocation — où je suis

Appuie sur Partager la position pour commencer.
Données: Open-Meteo + WeatherAPI • 24/7""",
        "time": "⏰ Ton heure locale: {time}\n📍 {city}",
        "dst": "⏰ Changement d'heure pour {city}\nActuel: {is_dst}\nProchain: {next_change}",
        "buttons": {"share": "📍 Partager position", "time": "⏰ Heure", "dst": "⏰ Heure d'été", "today": "🌤 Aujourd'hui", "week": "📅 Semaine"}
    },
    "be": {
        "greeting": """👋 Прывітанне! Я твой асабісты метэаролаг

Паказваю надвор'е дакладней за iPhone і ніколі не забываю пра перавод гадзінніка.

📍 ШТО Я ЎМЕЮ:

🌤 НАДВОР'Е:
- /current — зараз: тэмп, адчуваецца, вільготнасць
- /today — падрабязна на сёння
- /tomorrow — прагноз на заўтра
- /week — на 7 дзён наперад
- /hourly — па гадзінах на 24г
🔍 ДЭТАЛІ:
- /rain — дождж: шанец + мм
- /wind — вецер + парывах у м/с
- /sun — усход, захад, даўжыня дня
- /uv — УФ індэкс + парады
- /air — якасць паветра AQI
- /alerts — папярэджанні

⏰ ЧАС:
- /time — твой дакладны час
- /dst — лета/зіма + перавод гадзінніка

📍 ЛАКАЦЫЯ:
- /location — змяніць горад
- /mylocation — дзе я знаходжуся

Націсні Падзяліцца лакацыяй каб пачаць.
Дадзеныя: Open-Meteo + WeatherAPI • Працую 24/7""",
        "time": "⏰ Твой мясцовы час: {time}\n📍 {city}",
        "dst": "⏰ Перавод гадзінніка для {city}\nЗараз: {is_dst}\nНаступны: {next_change}",
        "buttons": {"share": "📍 Падзяліцца лакацыяй", "time": "⏰ Час", "dst": "⏰ Перавод", "today": "🌤 Сёння", "week": "📅 Тыдзень"}
    },
    "uk": {
        "greeting": """👋 Привіт! Я твій особистий метеоролог

Показую погоду точніше за iPhone і ніколи не забуваю про переведення годинника.

📍 ЩО Я ВМІЮ:

🌤 ПОГОДА:
- /current — зараз: темп, відчувається, вологість
- /today — детально на сьогодні
- /tomorrow — прогноз на завтра
- /week — на 7 днів вперед
- /hourly — по годинах на 24г

🔍 ДЕТАЛІ:
- /rain — дощ: шанс + мм
- /wind — вітер + пориви в м/с
- /sun — схід, захід, довжина дня
- /uv — УФ індекс + поради
- /air — якість повітря AQI
- /alerts — попередження

⏰ ЧАС:
- /time — твій точний час
- /dst — літо/зима + переведення годинника

📍 ЛОКАЦІЯ:
- /location — змінити місто
- /mylocation — де я знаходжуся

Натисни Поділитися локацією щоб почати.
Дані: Open-Meteo + WeatherAPI • Працюю 24/7""",
        "time": "⏰ Твій місцевий час: {time}\n📍 {city}",
        "dst": "⏰ Переведення годинника для {city}\nЗараз: {is_dst}\nНаступне: {next_change}",
        "buttons": {"share": "📍 Поділитися локацією", "time": "⏰ Час", "dst": "⏰ Переведення", "today": "🌤 Сьогодні", "week": "📅 Тиждень"}
    },
    "it": {
        "greeting": """👋 Ciao! Sono il tuo meteorologo personale

Mostro il meteo più preciso dell'iPhone e non dimentico mai il cambio dell'ora.

📍 COSA SO FARE:

🌤 METEO:
- /current — ora: temp, percepita, umidità
- /today — dettagliato oggi
- /tomorrow — previsioni domani
- /week — 7 giorni avanti
- /hourly — orario 24h

🔍 DETTAGLI:
- /rain — pioggia: probabilità + mm
- /wind — vento + raffiche in m/s
- /sun — alba, tramonto, durata giorno
- /uv — indice UV + consigli
- /air — qualità aria AQI
- /alerts — avvisi

⏰ ORARIO:
- /time — la tua ora esatta
- /dst — estate/inverno + cambio ora

📍 POSIZIONE:
- /location — cambia città
- /mylocation — dove mi trovo

Premi Condividi posizione per iniziare.
Dati: Open-Meteo + WeatherAPI • H24""",
        "time": "⏰ La tua ora locale: {time}\n📍 {city}",
        "dst": "⏰ Cambio ora per {city}\nAttuale: {is_dst}\nProssimo: {next_change}",
        "buttons": {"share": "📍 Condividi posizione", "time": "⏰ Ora", "dst": "⏰ Ora legale", "today": "🌤 Oggi", "week": "📅 Settimana"}
    },
    "de": {
        "greeting": """👋 Hi! Ich bin dein persönlicher Meteorologe

Ich zeige das Wetter genauer als das iPhone und vergesse nie die Zeitumstellung.

📍 WAS ICH KANN:

🌤 WETTER:
- /current — jetzt: Temp, gefühlt, Feuchte
- /today — detailliert heute
- /tomorrow — morgen Prognose
- /week — 7 Tage voraus
- /hourly — stündlich 24h

🔍 DETAILS:
- /rain — Regen: Chance + mm
- /wind — Wind + Böen in m/s
- /sun — Sonnenaufgang, -untergang, Tageslänge
- /uv — UV-Index + Tipps
- /air — Luftqualität AQI
- /alerts — Warnungen

⏰ ZEIT:
- /time — deine genaue Zeit
- /dst — Sommer/Winter + Zeitumstellung

📍 STANDORT:
- /location — Stadt ändern
- /mylocation — wo ich bin

Drücke Standort teilen zum Starten.
Daten: Open-Meteo + WeatherAPI • 24/7""",
        "time": "⏰ Deine Ortszeit: {time}\n📍 {city}",
        "dst": "⏰ Zeitumstellung für {city}\nAktuell: {is_dst}\nNächste: {next_change}",
        "buttons": {"share": "📍 Standort teilen", "time": "⏰ Zeit", "dst": "⏰ Zeitumstellung", "today": "🌤 Heute", "week": "📅 Woche"}
    },
    "sr": {
        "greeting": """👋 Zdravo! Ja sam tvoj lični meteorolog

Prikazujem vreme tačnije od iPhone-a i nikad ne zaboravljam pomeranje sata.

📍 ŠTA ZNAM:
🌤 VREME:
- /current — sada: temp, osećaj, vlažnost
- /today — detaljno danas
- /tomorrow — prognoza sutra
- /week — 7 dana unapred
- /hourly — po satima 24h

🔍 DETALJI:
- /rain — kiša: šansa + mm
- /wind — vetar + udari u m/s
- /sun — izlazak, zalazak, dužina dana
- /uv — UV indeks + saveti
- /air — kvalitet vazduha AQI
- /alerts — upozorenja

⏰ VREME:
- /time — tvoje tačno vreme
- /dst — leto/zima + pomeranje sata

📍 LOKACIJA:
- /location — promeni grad
- /mylocation — gde sam

Pritisni Podeli lokaciju za početak.
Podaci: Open-Meteo + WeatherAPI • 24/7""",
        "time": "⏰ Tvoje lokalno vreme: {time}\n📍 {city}",
        "dst": "⏰ Pomeranje sata za {city}\nTrenutno: {is_dst}\nSledeće: {next_change}",
        "buttons": {"share": "📍 Podeli lokaciju", "time": "⏰ Vreme", "dst": "⏰ Pomeranje", "today": "🌤 Danas", "week": "📅 Nedelja"}
    },
    "es": {
        "greeting": """👋 ¡Hola! Soy tu meteorólogo personal

Muestro el tiempo más preciso que el iPhone y nunca olvido el cambio de hora.

📍 LO QUE SÉ HACER:

🌤 TIEMPO:
- /current — ahora: temp, sensación, humedad
- /today — detallado hoy
- /tomorrow — pronóstico mañana
- /week — 7 días adelante
- /hourly — por horas 24h

🔍 DETALLES:
- /rain — lluvia: probabilidad + mm
- /wind — viento + ráfagas en m/s
- /sun — amanecer, anochecer, duración del día
- /uv — índice UV + consejos
- /air — calidad aire AQI
- /alerts — alertas

⏰ HORA:
- /time — tu hora exacta
- /dst — verano/invierno + cambio de hora

📍 UBICACIÓN:
- /location — cambiar ciudad
- /mylocation — donde estoy

Pulsa Compartir ubicación para empezar.
Datos: Open-Meteo + WeatherAPI • 24/7""",
        "time": "⏰ Tu hora local: {time}\n📍 {city}",
        "dst": "⏰ Cambio de hora para {city}\nActual: {is_dst}\nPróximo: {next_change}",
        "buttons": {"share": "📍 Compartir ubicación", "time": "⏰ Hora", "dst": "⏰ Cambio hora", "today": "🌤 Hoy", "week": "📅 Semana"}
    },
    "pl": {
        "greeting": """👋 Cześć! Jestem twoim osobistym meteorologiem

Pokazuję pogodę dokładniej niż iPhone i nigdy nie zapominam o zmianie czasu.

📍 CO POTRAFIĘ:

🌤 POGODA:
- /current — teraz: temp, odczuwalna, wilgotność
- /today — szczegółowo dziś
- /tomorrow — prognoza na jutro
- /week — 7 dni naprzód
- /hourly — godzinowo 24h

🔍 SZCZEGÓŁY:
- /rain — deszcz: szansa + mm
- /wind — wiatr + porywy w m/s
- /sun — wschód, zachód, długość dnia
- /uv — indeks UV + porady
- /air — jakość powietrza AQI
- /alerts — ostrzeżenia

⏰ CZAS:
- /time — twój dokładny czas
- /dst — lato/zima + zmiana czasu

📍 LOKALIZACJA:
- /location — zmień miasto
- /mylocation — gdzie jestem

Naciśnij Udostępnij lokalizację aby zacząć.
Dane: Open-Meteo + WeatherAPI • 24/7""",
        "time": "⏰ Twój czas lokalny: {time}\n📍 {city}",
        "dst": "⏰ Zmiana czasu dla {city}\nObecnie: {is_dst}\nNastępna: {next_change}",
        "buttons": {"share": "📍 Udostępnij lokalizację", "time": "⏰ Czas", "dst": "⏰ Zmiana czasu", "today": "🌤 Dziś", "week": "📅 Tydzień"}
    }
}

GREETINGS = {k: v["greeting"] for k, v in ALL_LANGUAGES.items()}
TIME_MSG = {k: v["time"] for k, v in ALL_LANGUAGES.items()}
DST_MSG = {k: v["dst"] for k, v in ALL_LANGUAGES.items()}
BUTTONS = {k: v["buttons"] for k, v in ALL_LANGUAGES.items()
