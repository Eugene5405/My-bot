MESSAGES = {
"en": """👋 Hi! I'm your personal meteorologist

I show weather more accurate than iPhone, and I never forget DST.

📍 WHAT I CAN DO:
🌤 WEATHER: /current /today /tomorrow /week /hourly
🔍 DETAILS: /rain /wind /sun /uv /air /alerts
⏰ TIME: /time /dst
📍 LOCATION: /location /mylocation

Press Share Location to start.
Data: Open-Meteo + WeatherAPI • Working 24/7""",
"ru": """👋 Привет! Я твой личный метеоролог
Я показываю погоду точнее чем iPhone и никогда не забываю про перевод часов.

📍 ЧТО Я УМЕЮ:
🌤 /current /today /tomorrow /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst - время + перевод часов
📍 /location /mylocation

Нажми Поделиться локацией.
Данные: Open-Meteo + WeatherAPI • 24/7""",
"sr": """👋 Zdravo! Ja sam tvoj lični meteorolog
Pokazujem vreme tačnije od iPhone-a i nikad ne zaboravljam pomeranje sata.

🌤 /current /today /tomorrow /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst
📍 /location

Pritisni Podeli lokaciju.
Podaci: Open-Meteo + WeatherAPI""",
"de": """👋 Hi! Ich bin dein persönlicher Meteorologe
Genauer als iPhone, vergesse nie Zeitumstellung.

🌤 /current /today /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst
📍 /location""",
"fr": """👋 Salut! Je suis ton météorologue personnel
Plus précis que l'iPhone, jamais oublié le changement d'heure.

🌤 /current /today /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst""",
"es": """👋 ¡Hola! Soy tu meteorólogo personal
Más preciso que iPhone, nunca olvido cambio de hora.

🌤 /current /today /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst""",
"it": """👋 Ciao! Sono il tuo meteorologo personale
Più preciso di iPhone, non dimentico mai ora legale.

🌤 /current /today /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst""",
"tr": """👋 Merhaba! Kişisel meteoroloğunum
iPhone'dan daha doğru, yaz saati unutmam.

🌤 /current /today /week /hourly
🔍 /rain /wind /sun /uv /air /alerts
⏰ /time /dst""",
"ar": """👋 مرحبا! أنا خبير الأرصاد الخاص بك
أدق من iPhone ولا أنسى تغيير الساعة.

🌤 /current /today /week /hourly
⏰ /time /dst""",
"zh": """👋 你好！我是你的私人气象员
比iPhone更准确，从不忘记夏令时。

🌤 /current /today /week /hourly
⏰ /time /dst"""
}

TIME_MSG = {
"en": "⏰ Your local time: {time}\n📍 {city}\n🌍 Timezone: {tz}",
"ru": "⏰ Твое местное время: {time}\n📍 {city}\n🌍 Часовой пояс: {tz}",
"sr": "⏰ Tvoje lokalno vreme: {time}\n📍 {city}\n🌍 Zona: {tz}",
"de": "⏰ Deine Ortszeit: {time}\n📍 {city}\n🌍 {tz}",
"fr": "⏰ Ton heure locale: {time}\n📍 {city}",
"es": "⏰ Tu hora local: {time}\n📍 {city}",
"it": "⏰ La tua ora locale: {time}\n📍 {city}",
"tr": "⏰ Yerel saatin: {time}\n📍 {city}",
"ar": "⏰ وقتك المحلي: {time}\n📍 {city}",
"zh": "⏰ 你的当地时间: {time}\n📍 {city}",
}

DST_MSG = {
"en": "⏰ DST for {city}\nCurrent: {is_dst}\nTimezone: {tz}\nNext change: {next_change}\nIn {days} days clocks go {direction} by 1h.\n\nI never forget DST 😉",
"ru": "⏰ Перевод часов для {city}\nСейчас: {is_dst}\nПояс: {tz}\nСледующий: {next_change}\nЧерез {days} дней часы {direction} на 1 час.\n\nЯ никогда не забываю 😉",
"sr": "⏰ Pomeranje sata za {city}\nTrenutno: {is_dst}\nSledeće: {next_change}\nZa {days} dana sat ide {direction}.",
}
