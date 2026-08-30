import os
import time
import random
import logging
import sqlite3
import urllib.parse
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    BotCommand,
    InputMediaVideo,
    InputMediaPhoto
)

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------
# RENDER WEB SERVICE & KEEP ALIVE
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online & Automated Admin Verification Active!"

@app.route('/ping')
def ping():
    return jsonify(status="alive", code=200)

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ---------------------------------------------------------
# BOT & CONFIGURATION
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "kushal_owner")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6632236983"))

MY_UPI_ID = os.environ.get("MY_UPI_ID", "paytm.s20glin@pty")
MY_UPI_NAME = os.environ.get("MY_UPI_NAME", "Viral MMS Store")

# Local QR Image Path (Apne folder ki file ka naam)
QR_IMAGE_PATH = "qr.jpg"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
DB_NAME = "bot_data.db"
admin_states = {}

# Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("admin", "Open Admin Control Panel"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    logging.error(f"Commands setup error: {e}")

# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    txn_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    username TEXT,
                    plan_name TEXT,
                    amount REAL,
                    status TEXT DEFAULT 'PENDING',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", 
              (user_id, username, first_name))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# KEYBOARD LAYOUTS & SECTIONS
# ---------------------------------------------------------
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💦 Real Indian Desi Porn 🫦", callback_data="p1"),
        InlineKeyboardButton("🌽 Ch1L CORN — ₹79 / 30d", callback_data="p2"),
        InlineKeyboardButton("✨ CORE R@PE 3 3 — ₹96 / 30d", callback_data="p3"),
        InlineKeyboardButton("✨ ALL VIDEO VIP MEMBER ✨ — ₹155 / 30d", callback_data="p4"),
        InlineKeyboardButton("🥳 BHAI BHEN HOT 🥳 — ₹89 / 365d", callback_data="p5"),
        InlineKeyboardButton("🥵 HOT DESI BHABHI 6 🥵 — ₹111 / 60d", callback_data="p6"),
        InlineKeyboardButton("😳 INFLUENCER 50%-OFF 7 🥵 — ₹129 / 60d", callback_data="p7"),
        InlineKeyboardButton("🔞 PAID PACK 🔞 — ₹88 / 30d", callback_data="p8"),
        InlineKeyboardButton("🔴 VVIP PLAN 1 LAKH VIDEO — ₹277 / 365d", callback_data="p10")
    )
    return markup

def get_product_buy_keyboard(plan_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Buy Now", callback_data=f"buy_{plan_id}"),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    )
    return markup

def get_payment_action_keyboard(txn_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("✅ Check Payment Status", callback_data=f"chkpay_{txn_id}"),
        InlineKeyboardButton("❌ Cancel Payment", callback_data="back")
    )
    return markup

sections = {
    "p1": {"name": "💦 Real Indian Desi Porn 🫦", "price": "69", "validity": "30 Days"},
    "p2": {"name": "🌽 Ch1L CORN 🌽", "price": "79", "validity": "30 Days"},
    "p3": {"name": "✨ CORE R@PE 3 3 ✨", "price": "96", "validity": "30 Days"},
    "p4": {"name": "✨ ALL VIDEO VIP MEMBER ✨", "price": "155", "validity": "30 Days"},
    "p5": {"name": "🥳 BHAI BHEN HOT 🥳", "price": "89", "validity": "365 Days"},
    "p6": {"name": "🥵 HOT DESI BHABHI 6 🥵", "price": "111", "validity": "60 Days"},
    "p7": {"name": "😳 INFLUENCER 50%-OFF 7 🥵", "price": "129", "validity": "60 Days"},
    "p8": {"name": "🔞 PAID PACK 🔞", "price": "88", "validity": "30 Days"},
    "p10": {"name": "🔴 VVIP PLAN 1 LAKH VIDEO 🔴", "price": "277", "validity": "365 Days"}
}

# ---------------------------------------------------------
# DIRECT LOCAL FOLDER QR IMAGE SENDER
# ---------------------------------------------------------
def send_payment_qr(chat_id, plan_info, username):
    txn_id = str(random.randint(100000000000000, 999999999999999))
    plan_name = plan_info["name"]
    amount = float(plan_info["price"])
    validity = plan_info["validity"]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (txn_id, user_id, username, plan_name, amount) VALUES (?, ?, ?, ?, ?)",
              (txn_id, chat_id, username, plan_name, amount))
    conn.commit()
    conn.close()

    payment_caption = (
        f"💳 **Scan & Pay**\n\n"
        f"📦 Plan: **{plan_name}**\n"
        f"💰 Amount: **₹{amount}**\n"
        f"⏳ Validity: **{validity}**\n\n"
        f"🧾 Transaction ID:\n`{txn_id}`\n\n"
        f"📲 **Scan the QR above** & pay the exact amount.\n"
        f"✅ After paying, tap **Check Payment Status** below."
    )

    # Directly check and send local folder image file
    if os.path.exists(QR_IMAGE_PATH):
        with open(QR_IMAGE_PATH, 'rb') as photo_file:
            bot.send_photo(chat_id, photo=photo_file, caption=payment_caption, reply_markup=get_payment_action_keyboard(txn_id))
    else:
        # Fallback QR Generator if local file isn't uploaded yet
        encoded_name = urllib.parse.quote(MY_UPI_NAME)
        upi_url = f"upi://pay?pa={MY_UPI_ID}&pn={encoded_name}&am={amount}&cu=INR"
        qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={urllib.parse.quote(upi_url)}"
        bot.send_photo(chat_id, photo=qr_api, caption=payment_caption, reply_markup=get_payment_action_keyboard(txn_id))

# ---------------------------------------------------------
# COMMAND & HANDLERS
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "User"
    add_user(message.chat.id, username, first_name)
    
    welcome_msg = f"👋 Hello **{first_name}**!\n\nChoose a plan below to get started:"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data in sections:
        sec = sections[data]
        caption = f"📦 **{sec['name']}**\n💰 Price: ₹{sec['price']} | ⏱️ {sec['validity']}"
        bot.send_message(chat_id, caption, reply_markup=get_product_buy_keyboard(data))

    elif data.startswith("buy_"):
        plan_id = data.split("_")[1]
        username = call.from_user.username or "No Username"
        if plan_id in sections:
            send_payment_qr(chat_id, sections[plan_id], username)

    elif data.startswith("chkpay_"):
        txn_id = data.split("_")[1]
        bot.send_message(chat_id, "⏳ Payment status request sent to Admin!")
        bot.send_message(
            ADMIN_ID, 
            f"🔔 **New Verification Request!**\n\nUser ID: `{chat_id}`\nTxn ID: `{txn_id}`"
        )

    elif data == "back":
        bot.send_message(chat_id, "Main Menu:", reply_markup=get_main_keyboard())

if __name__ == '__main__':
    keep_alive()
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(non_stop=True)
    import os
import time
import random
import logging
import sqlite3
import urllib.parse
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    BotCommand
)

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------
# RENDER WEB SERVICE & KEEP ALIVE
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online & Automated Admin Verification Active!"

@app.route('/ping')
def ping():
    return jsonify(status="alive", code=200)

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ---------------------------------------------------------
# BOT & CONFIGURATION
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "kushal_owner")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6632236983"))

MY_UPI_ID = os.environ.get("MY_UPI_ID", "paytm.s20glin@pty")
MY_UPI_NAME = os.environ.get("MY_UPI_NAME", "Viral MMS Store")
MY_QR_IMAGE = "https://i.ibb.co/Mk2DmrYd/image.jpg"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
DB_NAME = "bot_data.db"
admin_states = {}

# Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("admin", "Open Admin Control Panel"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    logging.error(f"Commands setup error: {e}")

# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    txn_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    username TEXT,
                    plan_name TEXT,
                    amount REAL,
                    status TEXT DEFAULT 'PENDING',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", 
              (user_id, username, first_name))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# KEYBOARD LAYOUTS & SECTIONS
# ---------------------------------------------------------
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💦 Real Indian Desi Porn 🫦", callback_data="p1"),
        InlineKeyboardButton("🌽 Ch1L CORN — ₹79 / 30d", callback_data="p2"),
        InlineKeyboardButton("✨ CORE R@PE 3 3 — ₹96 / 30d", callback_data="p3"),
        InlineKeyboardButton("✨ ALL VIDEO VIP MEMBER ✨ — ₹155 / 30d", callback_data="p4"),
        InlineKeyboardButton("🥳 BHAI BHEN HOT 🥳 — ₹89 / 365d", callback_data="p5"),
        InlineKeyboardButton("🥵 HOT DESI BHABHI 6 🥵 — ₹111 / 60d", callback_data="p6"),
        InlineKeyboardButton("😳 INFLUENCER 50%-OFF 7 🥵 — ₹129 / 60d", callback_data="p7"),
        InlineKeyboardButton("🔞 PAID PACK 🔞 — ₹88 / 30d", callback_data="p8"),
        InlineKeyboardButton("🔴 VVIP PLAN 1 LAKH VIDEO — ₹277 / 365d", callback_data="p10")
    )
    return markup

def get_product_buy_keyboard(plan_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Buy Now", callback_data=f"buy_{plan_id}"),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    )
    return markup

def get_payment_action_keyboard(txn_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("✅ Check Payment Status", callback_data=f"chkpay_{txn_id}"),
        InlineKeyboardButton("❌ Cancel Payment", callback_data="back")
    )
    return markup

sections = {
    "p1": {"name": "💦 Real Indian Desi Porn 🫦", "price": "69", "validity": "30 Days"},
    "p2": {"name": "🌽 Ch1L CORN 🌽", "price": "79", "validity": "30 Days"},
    "p3": {"name": "✨ CORE R@PE 3 3 ✨", "price": "96", "validity": "30 Days"},
    "p4": {"name": "✨ ALL VIDEO VIP MEMBER ✨", "price": "155", "validity": "30 Days"},
    "p5": {"name": "🥳 BHAI BHEN HOT 🥳", "price": "89", "validity": "365 Days"},
    "p6": {"name": "🥵 HOT DESI BHABHI 6 🥵", "price": "111", "validity": "60 Days"},
    "p7": {"name": "😳 INFLUENCER 50%-OFF 7 🥵", "price": "129", "validity": "60 Days"},
    "p8": {"name": "🔞 PAID PACK 🔞", "price": "88", "validity": "30 Days"},
    "p10": {"name": "🔴 VVIP PLAN 1 LAKH VIDEO 🔴", "price": "277", "validity": "365 Days"}
}

# ---------------------------------------------------------
# PAYMENT QR SENDER (PAYTM QR IMAGE)
# ---------------------------------------------------------
def send_payment_qr(chat_id, plan_info, username):
    txn_id = str(random.randint(100000000000000, 999999999999999))
    plan_name = plan_info["name"]
    amount = float(plan_info["price"])
    validity = plan_info["validity"]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (txn_id, user_id, username, plan_name, amount) VALUES (?, ?, ?, ?, ?)",
              (txn_id, chat_id, username, plan_name, amount))
    conn.commit()
    conn.close()

    payment_caption = (
        f"💳 **Scan & Pay**\n\n"
        f"📦 Plan: **{plan_name}**\n"
        f"💰 Amount: **₹{amount}**\n"
        f"⏳ Validity: **{validity}**\n\n"
        f"🧾 Transaction ID:\n`{txn_id}`\n\n"
        f"📲 **Scan the QR above** & pay the exact amount.\n"
        f"✅ After paying, tap **Check Payment Status** below."
    )

    try:
        bot.send_photo(chat_id, photo=MY_QR_IMAGE, caption=payment_caption, reply_markup=get_payment_action_keyboard(txn_id))
    except Exception as e:
        bot.send_message(chat_id, payment_caption, reply_markup=get_payment_action_keyboard(txn_id))

# ---------------------------------------------------------
# COMMAND & HANDLERS
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "User"
    add_user(message.chat.id, username, first_name)
    
    welcome_msg = f"👋 Hello **{first_name}**!\n\nChoose a plan below to get started:"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data in sections:
        sec = sections[data]
        caption = f"📦 **{sec['name']}**\n💰 Price: ₹{sec['price']} | ⏱️ {sec['validity']}"
        bot.send_message(chat_id, caption, reply_markup=get_product_buy_keyboard(data))

    elif data.startswith("buy_"):
        plan_id = data.split("_")[1]
        username = call.from_user.username or "No Username"
        if plan_id in sections:
            send_payment_qr(chat_id, sections[plan_id], username)

    elif data.startswith("chkpay_"):
        txn_id = data.split("_")[1]
        bot.send_message(chat_id, "⏳ Payment status request sent to Admin!")
        bot.send_message(
            ADMIN_ID, 
            f"🔔 **New Verification Request!**\n\nUser ID: `{chat_id}`\nTxn ID: `{txn_id}`"
        )

    elif data == "back":
        bot.send_message(chat_id, "Main Menu:", reply_markup=get_main_keyboard())

if __name__ == '__main__':
    keep_alive()
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(non_stop=True)
