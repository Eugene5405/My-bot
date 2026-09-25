from telegram import Update
from telegram.ext import ContextTypes
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang
from datetime import datetime
import pytz

async def dst_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    tpl = data["dst"]
    
    # пока заглушка - потом подключим реальный город
    city = "Belgrade"
    tz = "Europe/Belgrade"
    
    text = tpl.format(
        city=city,
        is_dst="Summer Time",
        dst_status="DST ON",
        tz=tz,
        next_change="26 Oct 2025 03:00",
        days=30,
        direction="back"
    )
    await update.message.reply_text(text)

async def time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    tpl = data["time"]
    
    now = datetime.now(pytz.timezone("Europe/Belgrade")).strftime("%H:%M:%S")
    
    text = tpl.format(time=now, city="Belgrade", tz="Europe/Belgrade", offset="+02:00")
    await update.message.reply_text(text)
