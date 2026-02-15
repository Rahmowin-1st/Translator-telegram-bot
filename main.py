# =========================================
# TELEGRAM AI TRANSLATOR BOT - MONOLITH
# =========================================

import asyncio
import logging
import sqlite3
import asyncio
import datetime
import base64
import json
import threading
from io import BytesIO

import requests
from flask import Flask, request, redirect

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from gtts import gTTS
from google import genai
from google.genai import types

# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================================
# CONFIG
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7591558748:AAH-idabaw_3JlEYpdA4QhPhpOoLVOqAVnk"
AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

client = genai.Client(
    api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
    http_options={
        'api_version': '',
        'base_url': AI_INTEGRATIONS_GEMINI_BASE_URL   
    }
)

ADMIN_IDS = [7324243811]
DB_NAME = "ultimate_bot.db"

# =========================================
# LANGUAGE SYSTEM
# =========================================

POPULAR_CODES = ["uz","en","ru","tg","es","ko","ar","ja","fr","de"]

LANG_NAMES = {
    "uz": {
        "uz":"O'zbekcha 🇺🇿","en":"Inglizcha 🇺🇸","ru":"Ruscha 🇷🇺","tg":"Tojikcha 🇹🇯",
        "es":"Ispancha 🇪🇸","ko":"Koreyscha 🇰🇷","ar":"Arabcha 🇦🇪","ja":"Yaponcha 🇯🇵",
        "fr":"Fransuzcha 🇫🇷","de":"Nemischa 🇩🇪","auto":"Auto"
    },
    "en": {
        "uz":"Uzbek 🇺🇿","en":"English 🇺🇸","ru":"Russian 🇷🇺","tg":"Tajik 🇹🇯",
        "es":"Spanish 🇪🇸","ko":"Korean 🇰🇷","ar":"Arabic 🇦🇪","ja":"Japanese 🇯🇵",
        "fr":"French 🇫🇷","de":"German 🇩🇪","auto":"Auto"
    },
    "ru": {
        "uz":"Узбекский 🇺🇿","en":"Английский 🇺🇸","ru":"Русский 🇷🇺","tg":"Таджикский 🇹🇯",
        "es":"Испанский 🇪🇸","ko":"Корейский 🇰🇷","ar":"Арабский 🇦🇪","ja":"Японский 🇯🇵",
        "fr":"Французский 🇫🇷","de":"Немецкий 🇩🇪","auto":"Auto"
    }
}

TEXTS = {
    "uz":{
        "start":"🚀 Xush kelibsiz! Matn, rasm yoki ovoz yuboring, men uni avtomatik aniqlab tarjima qilib beraman.",
        "tr_ask":"🌍 Qaysi tilga tarjima qilamiz?",
        "settings":"⚙️ Sozlamalar",
        "help_main":"ℹ️ Yordam: Matn, rasm yoki ovoz yuboring. Men uni avtomatik aniqlab tarjima qilaman.",
        "help_settings":"ℹ️ Bu yerda siz bot tilini va tarjima qilinadigan tilni sozlashingiz mumkin.",
        "premium":"💎 Premium",
        "advice":"📩 Maslahat",
        "lang_select":"🌍 Sistema tilini tanlang:",
        "saved_lang":"💾 Saqlangan til ({lang})",
        "processing":"⏳ Tarjima qilinmoqda...",
        "detected_label":"🔍 Aniqlangan til",
        "target_label":"🎯 Tarjima tili",
        "more_options":"➕ Batafsil",
        "explain_btn"Ma'nosi'nosi",
        "synonym_btn":"📚 Sinonimlar",
        "other_lang_btn":"🌍 Boshqa til",
        "admin_stats":"📊 Statistika",
        "admin_broadcast":"📢 Reklama",
        "admin_info":"ℹ️ Admin buyruqlari:\n/stats - Statistika\n/broadcast [matn] - Hamma foydalanuvchilarga xabar\n/users - Foydalanuvchilar ro'yxati\n/db - Bazani yuklab olish",
        "invalid_text":"❌ Noto'g'ri matn!"
    },
    "en":{
        "start":"🚀 Welcome! Send text, image or voice, and I will automatically detect and translate it.",
        "tr_ask":"🌍 Select target language:",
        "settings":"⚙️ Settings",
        "help_main":"ℹ️ Help: Send text, image or voice. I'll detect and translate it automatically.",
        "help_settings":"ℹ️ Here you can configure the system language and default translation language.",
        "premium":"💎 Premium",
        "advice":"📩 Advice",
        "lang_select":"🌍 Select system language:",
        "saved_lang":"💾 Saved language ({lang})",
        "processing":"⏳ Translating...",
        "detected_label":"🔍 Detected language",
        "target_label":"🎯 Target language",
        "more_options":"➕ More",
        "explain_btn":"📖 Meaning",
        "synonym_btn":"📚 Synonyms",
        "other_lang_btn":"🌍 Other language",
        "admin_stats":"📊 Stats",
        "admin_broadcast":"📢 Broadcast",
        "admin_info":"ℹ️ Admin Commands:\n/stats - Show stats\n/broadcast [text] - Send message to all\n/users - List users\n/db - Download database",
        "invalid_text":"❌ Invalid text!"
    },
    "ru":{
        "start":"🚀 Добро пожаловать! Отправьте текст, фото или голос, и я автоматически переведу их.",
        "tr_ask":"🌍 Выберите язык перевода:",
        "settings":"⚙️ Настройки",
        "help_main":"ℹ️ Помощь: Отправьте текст, фото или голос. Я автоматически определю язык и переведу.",
        "help_settings":"ℹ️ Здесь вы можете настроить язык бота и язык перевода по умолчанию.",
        "premium":"💎 Премиум",
        "advice":"📩 Совет",
        "lang_select":"🌍 Выберите системный язык:",
        "saved_lang":"💾 Сохраненный язык ({lang})",
        "processing":"⏳ Перевод...",
        "detected_label":"🔍 Определенный язык",
        "target_label":"🎯 Язык перевода",
        "more_options":"➕ Подробнее",
        "explain_btn":"📖 Значение",
        "synonym_btn":"📚 Синонимы",
        "other_lang_btn":"🌍 Другой язык",
        "admin_stats":"📊 Статистика",
        "admin_broadcast":"📢 Рассылка",
        "admin_info":"ℹ️ Команды админа:\n/stats - Статистика\n/broadcast [текст] - Рассылка всем\n/users - Список пользователей\n/db - Скачать базу",
        "invalid_text":"❌ Неверный текст!"
    }
}

# =========================================
# DATABASE
# =========================================

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, joined_date TEXT,
        system_lang TEXT DEFAULT 'uz', last_target_lang TEXT DEFAULT 'en',
        premium INTEGER DEFAULT 0, blocked INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, role TEXT, content TEXT,
        detected_lang TEXT, target_lang TEXT, created_at TEXT
    )""")
    conn.commit()
    conn.close()

def get_user(uid, full_name="", username=""):
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users(user_id,username,full_name,joined_date) VALUES(?,?,?,?)",
                  (uid, username or "", full_name or "", datetime.datetime.now().isoformat()))
        conn.commit()
        return get_user(uid)
    conn.close()
    return {"user_id": row[0], "username": row[1], "full_name": row[2], "system_lang": row[4], "last_target_lang": row[5], "premium": row[6]}

def update_user(uid, **kwargs):
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    for k,v in kwargs.items():
        c.execute(f"UPDATE users SET {k}=? WHERE user_id=?", (v,uid))
    conn.commit()
    conn.close()

def save_history(uid, role, content, det="auto", target="auto"):
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("INSERT INTO history(user_id,role,content,detected_lang,target_lang,created_at) VALUES(?,?,?,?,?,?)",
                 (uid,role,content,det,target,datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# =========================================
# AI ENGINE
# =========================================

def gemini_call(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=8192)
        )
        return response.text.strip() if response.text else ""
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return ""

def gemini_vision(img_b64):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Identify and translate the text in this image. Return ONLY the translation.", 
                      types.Part(inline_data=types.Blob(mime_type="image/png", data=img_b64))]
        )
        return response.text.strip() if response.text else ""
    except Exception as e:
        return f"Error: {e}"

# =========================================
# KEYBOARDS
# =========================================

def main_kb(user):
    lang = user["system_lang"]
    target = user["last_target_lang"]
    target_name = LANG_NAMES[lang].get(target, target)
    kb = [
        [KeyboardButton(TEXTS[lang]["saved_lang"].format(lang=target_name))],
        [KeyboardButton(TEXTS[lang]["help_main"]), KeyboardButton(TEXTS[lang]["premium"])],
        [KeyboardButton(TEXTS[lang]["advice"]), KeyboardButton(TEXTS[lang]["settings"])]
    ]
    if user["user_id"] in ADMIN_IDS:
        kb.append([KeyboardButton(TEXTS[lang]["admin_stats"]), KeyboardButton(TEXTS[lang]["admin_broadcast"])])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def more_inline(lang, text_id):
    t = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["explain_btn"], callback_data=f"exp_{text_id}"),
         InlineKeyboardButton(t["synonym_btn"], callback_data=f"syn_{text_id}")],
        [InlineKeyboardButton(t["other_lang_btn"], callback_data=f"other_{text_id}")]
    ])

# =========================================
# HANDLERS
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message: return
    user = get_user(update.effective_user.id, update.effective_user.full_name, update.effective_user.username)
    await update.message.reply_text(TEXTS[user["system_lang"]]["start"], reply_markup=main_kb(user))

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id not in ADMIN_IDS: return
    conn = sqlite3.connect(DB_NAME)
    u_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    m_count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    conn.close()
    await update.message.reply_text(f"📊 Statistika:\nFoydalanuvchilar: {u_count}\nJami xabarlar: {m_count}")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id not in ADMIN_IDS: return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("📢 Foydalanish: /broadcast [matn]")
        return
    conn = sqlite3.connect(DB_NAME)
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(u[0], text)
            count += 1
        except: pass
    await update.message.reply_text(f"✅ {count} ta foydalanuvchiga yuborildi.")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id not in ADMIN_IDS: return
    conn = sqlite3.connect(DB_NAME)
    users = conn.execute("SELECT user_id, username, full_name FROM users ORDER BY joined_date DESC LIMIT 50").fetchall()
    conn.close()
    res = "👥 Oxirgi 50 foydalanuvchi:\n"
    for u in users:
        res += f"ID: {u[0]} | @{u[1]} | {u[2]}\n"
    if len(res) > 4096: res = res[:4090] + "..."
    await update.message.reply_text(res)

async def db_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id not in ADMIN_IDS: return
    with open(DB_NAME, 'rb') as f:
        await update.message.reply_document(f, filename=DB_NAME)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message: return
    uid = update.effective_user.id
    user = get_user(uid)
    lang = user["system_lang"]
    text = update.message.text.strip() if update.message.text else ""

    if text.startswith("💾"):
        rows = []
        for i in range(0, len(POPULAR_CODES), 2):
            row = [InlineKeyboardButton(LANG_NAMES[lang].get(c, c), callback_data=f"settr_{c}") for c in POPULAR_CODES[i:i+2]]
            rows.append(row)
        await update.message.reply_text(TEXTS[lang]["tr_ask"], reply_markup=InlineKeyboardMarkup(rows))
        return

    if text == TEXTS[lang]["settings"]:
        kb = [[InlineKeyboardButton(n[data], callback_data=f"sys_{data}")] for data, n in LANG_NAMES.items() if data != 'auto']
        await update.message.reply_text(TEXTS[lang]["lang_select"], reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == TEXTS[lang]["help_main"]:
        await update.message.reply_text(TEXTS[lang]["help_main"])
        return

    if text == TEXTS[lang]["admin_stats"] and uid in ADMIN_IDS:
        await stats_cmd(update, context)
        return

    if text == TEXTS[lang]["admin_broadcast"] and uid in ADMIN_IDS:
        await update.message.reply_text("📢 Broadcast uchun /broadcast [matn] buyrug'idan foydalaning.")
        return

    if text == TEXTS[lang]["premium"]:
        await update.message.reply_text("💎 Premium xizmatlar tez kunda...")
        return

    if text == TEXTS[lang]["advice"]:
        context.user_data["mode"] = "advice"
        await update.message.reply_text("📩 Maslahatingizni yozib qoldiring:")
        return

    if context.user_data.get("mode") == "advice":
        context.user_data["mode"] = None
        for admin in ADMIN_IDS:
            try: await context.bot.send_message(admin, f"📩 Maslahat (@{user['username']}):\n{text}")
            except: pass
        await update.message.reply_text("✅ Rahmat! Maslahatingiz yuborildi.")
        return

    # Default: Translate
    await translate_process(update, context, user, text)

async def translate_process(update: Update, context: ContextTypes.DEFAULT_TYPE, user, text, target=None):
    if not update.message: return
    uid = user["user_id"]
    lang = user["system_lang"]
    target = target or user["last_target_lang"]
    
    msg = await update.message.reply_text(TEXTS[lang]["processing"])
    
    det = gemini_call(f"Return ONLY the ISO 639-1 language code for this text: {text}")
    if not det or len(det) > 5: det = "auto"
    
    if det == target:
        target = "en" if det != "en" else "uz"

    res = gemini_call(f"Translate the following text to {target}. Return ONLY the translated text, no other comments: {text}")
    
    save_history(uid, "user", text, det, target)
    save_history(uid, "assistant", res, det, target)
    
    out = f"{TEXTS[lang]['detected_label']}: {LANG_NAMES[lang].get(det, det)}\n"
    out += f"{TEXTS[lang]['target_label']}: {LANG_NAMES[lang].get(target, target)}\n\n"
    out += f"✅ {res}\n\n{TEXTS[lang]['more_options']}:"
    
    history_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    context.bot_data[f"text_{history_id}"] = text
    context.bot_data[f"res_{history_id}"] = res
    context.bot_data[f"target_{history_id}"] = target

    await msg.edit_text(out, reply_markup=more_inline(lang, history_id))
    
    try:
        voice = gTTS(text=res, lang=target)
        bio = BytesIO()
        voice.write_to_fp(bio)
        bio.seek(0)
        await update.message.reply_voice(bio)
    except: pass

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.callback_query.from_user: return
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user = get_user(uid)
    lang = user["system_lang"]
    data = query.data or ""

    if data.startswith("sys_"):
        new_sys = data.replace("sys_", "")
        update_user(uid, system_lang=new_sys)
        user["system_lang"] = new_sys
        if query.message: await query.message.delete()
        await context.bot.send_message(uid, TEXTS[new_sys]["start"], reply_markup=main_kb(user))
    
    elif data.startswith("settr_"):
        new_tr = data.replace("settr_", "")
        update_user(uid, last_target_lang=new_tr)
        if query.message: await query.message.edit_text(f"✅ {LANG_NAMES[lang].get(new_tr, new_tr)}")

    elif data.startswith("exp_"):
        tid = data.replace("exp_", "")
        txt = context.bot_data.get(f"res_{tid}")
        if txt:
            res = gemini_call(f"Explain the meaning of this text in {lang} language: {txt}")
            await context.bot.send_message(uid, f"📖 {res}")

    elif data.startswith("syn_"):
        tid = data.replace("syn_", "")
        txt = context.bot_data.get(f"res_{tid}")
        if txt:
            res = gemini_call(f"Give synonyms for this text in the original language: {txt}")
            await context.bot.send_message(uid, f"📚 {res}")

    elif data.startswith("other_"):
        tid = data.replace("other_", "")
        txt = context.bot_data.get(f"text_{tid}")
        rows = []
        for i in range(0, len(POPULAR_CODES), 2):
            row = [InlineKeyboardButton(LANG_NAMES[lang].get(c, c), callback_data=f"trdirect_{c}_{tid}") for c in POPULAR_CODES[i:i+2]]
            rows.append(row)
        await context.bot.send_message(uid, TEXTS[lang]["tr_ask"], reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("trdirect_"):
        parts = data.split("_")
        target = parts[1]
        tid = parts[2]
        txt = context.bot_data.get(f"text_{tid}")
        if txt:
            res = gemini_call(f"Translate this text to {target}: {txt}")
            await context.bot.send_message(uid, f"🌍 {LANG_NAMES[lang].get(target, target)}: {res}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.photo: return
    uid = update.effective_user.id
    user = get_user(uid)
    lang = user["system_lang"]
    file = await update.message.photo[-1].get_file()
    buf = await file.download_as_bytearray()
    b64 = base64.b64encode(buf).decode()
    
    msg = await update.message.reply_text(TEXTS[lang]["processing"])
    res = gemini_vision(b64)
    await msg.edit_text(f"🖼 {res}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or not update.message.voice: return
    uid = update.effective_user.id
    user = get_user(uid)
    lang = user["system_lang"]
    file = await update.message.voice.get_file()
    buf = await file.download_as_bytearray()
    
    msg = await update.message.reply_text(TEXTS[lang]["processing"])
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="Transcribe this audio, returning ONLY the transcribed text."),
                    types.Part.from_bytes(data=buf, mime_type="audio/ogg")
                ]
            )
        ]
    )
    txt = response.text or ""
    await msg.edit_text(f"🎤 {txt}")

# =========================================
# FLASK & BOT START
# =========================================

flask_app = Flask(__name__)
@flask_app.route("/")
def home(): return "Bot is running!"

async def run_bot():
    init_db()
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=5000), daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("users", users_cmd))
    app.add_handler(CommandHandler("db", db_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.initialize()
    await app.start()
    if app.updater: await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_bot())
