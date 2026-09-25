from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.language import get_user_lang
from bot.utils.messages import TIME_MSG, DST_MSG
from bot.utils.storage import get_user_location
from bot.services.timezone import get_local_time

async def time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    loc = get_user_location(update.effective_user.id)
    if not loc:
        await update.message.reply_text("📍 Share location first / Сначала поделись локацией")
        return
    lt = get_local_time(loc['lat'], loc['lon'])
    tpl = TIME_MSG.get(lang, TIME_MSG["en"])
    await update.message.reply_text(tpl.format(
        time=lt.strftime("%H:%M:%S %d.%m.%Y"),
        city=loc.get('city','Location'),
        tz=lt.tzname()
    ))

async def dst_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    loc = get_user_location(update.effective_user.id)
    if not loc:
        await update.message.reply_text("📍 Share location first")
        return
    tpl = DST_MSG.get(lang, DST_MSG["en"])
    await update.message.reply_text(tpl.format(
        city=loc.get('city','Belgrade'),
        is_dst="Summer ☀️ / Летнее",
        tz="Europe/Belgrade",
        next_change="26 Oct 03:00 -> 02:00",
        days="30",
        direction="назад / back"
    ))
