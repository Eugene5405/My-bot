# запоминает язык юзера
USER_LANGS = {}

def get_user_lang(user_id):
    return USER_LANGS.get(user_id, "en")

def set_user_lang(user_id, lang):
    USER_LANGS[user_id] = lang
