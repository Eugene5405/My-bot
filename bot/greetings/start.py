from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.languages.messages import ALL_LANGUAGES
from bot.utils.language import get_user_lang

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    data = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])
    
    text = data["greeting"]
    btn = data["buttons"]
    
    keyboard = [
        [KeyboardButton(btn["share"], request_location=True)],
        [KeyboardButton(btn["today"]), KeyboardButton(btn["week"])],
        [KeyboardButton(btn["time"]), KeyboardButton(btn["dst"])]
    ]
    
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
