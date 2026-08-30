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
MY_QR_IMAGE = "https://i.ibb.co/Mk2DmrYd/image.jpg"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
DB_NAME = "bot_data.db"
users_list = set()
pending_verifications = {}
admin_states = {}

# Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
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
# KEYBOARD LAYOUTS
# ---------------------------------------------------------
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💦 Real Indian Dēsi Porn 👄", callback_data="p1"),
        InlineKeyboardButton("🌽 Ch1L CORN — ₹79 / 30d", callback_data="p2"),
        InlineKeyboardButton("✨ CORE R@PE 3 3 — ₹96 / 30d", callback_data="p3"),
        InlineKeyboardButton("✨ ALL VIDEO VIP MEMBER ✨ — ₹155 / 30d", callback_data="p4"),
        InlineKeyboardButton("🥳 BHAI BHEN HOT 🥳 — ₹89 / 365d", callback_data="p5"),
        InlineKeyboardButton("🥵 HOT DESI BHABHI 6 🥵 — ₹111 / 60d", callback_data="p6"),
        InlineKeyboardButton("😳 INFLUENCER 50%-OFF 7 🥵 — ₹129 / 60d", callback_data="p7"),
        InlineKeyboardButton("🔞 PAID PACK 🔞 — ₹88 / 30d", callback_data="p8"),
        InlineKeyboardButton("😍 VVIP PLAN 1 LAKH VIDEO — ₹277 / 365d", callback_data="p10")
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

def get_admin_approval_keyboard(user_id, txn_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Verify Payment", callback_data=f"adm_approve_{user_id}_{txn_id}"),
        InlineKeyboardButton("❌ Cancel Payment", callback_data=f"adm_reject_{user_id}_{txn_id}")
    )
    return markup

def get_media_object(f_path):
    if os.path.exists(f_path):
        if f_path.endswith(('.mp4', '.mkv', '.mov')):
            return InputMediaVideo(open(f_path, 'rb'), supports_streaming=True)
        elif f_path.endswith(('.jpg', '.jpeg', '.png')):
            return InputMediaPhoto(open(f_path, 'rb'))
    return None

# ---------------------------------------------------------
# START SEQUENCE & MEDIA SENDER
# ---------------------------------------------------------
def send_start_sequence(chat_id, user_name):
    start_files = [
        "videos/video1.mp4",
        "videos/photo1.jpg",
        "videos/video2.mp4",
        "videos/video3.mp4",
        "videos/video4.mp4"
    ]
    album = []
    for f in start_files:
        obj = get_media_object(f)
        if obj:
            album.append(obj)

    if len(album) > 0:
        try:
            bot.send_media_group(chat_id, album)
        except Exception as e:
            logging.error(f"Start Media Group Error: {e}")

    # Aapka updated text yahan set kiya gaya hai
    quality_text = (
        "✨ **TRY OUR ANY PLAN FOR CHECKING THE QUALITY** ✨ 🎉 Welcome to VIP Access Bot!\n\n"
        "✨ Get exclusive access to premium content\n"
        "💰 Affordable plans starting at just ₹99\n"
        "✨ Cotent quality aisi ki dekhi nahi hogi\n"
        "✨ Only Premium Content\n"
        "✨ Daily New Uploads\n"
        "✨ Cp, Rp, Indian, Foreign, Dark everything\n"
        "✨ 10000+ Cp videos\n"
        "✨ 25000+ Rp videos\n"
        "✨ M0m S0n 5k Videos\n\n"
        "✨ **TRY OUR ANY PLAN FOR CHECKING THE QUALITY** ✨"
    )
    bot.send_message(chat_id, quality_text)

    welcome_msg = f"👋 Hello, 🦋💸**{user_name}**!\n\nChoose a plan to get started:"
    bot.send_message(chat_id, welcome_msg, reply_markup=get_main_keyboard())

sections = {
    "p1": {"name": "💦 Real Indian Dēsi Porn 👄", "price": "69", "validity": "30 Days"},
    "p2": {"name": "🌽 Ch1L CORN 🌽", "price": "79", "validity": "30 Days"},
    "p3": {"name": "✨ CORE R@PE 3 3 ✨", "price": "96", "validity": "30 Days"},
    "p4": {"name": "✨ ALL VIDEO VIP MEMBER ✨", "price": "155", "validity": "30 Days"},
    "p5": {"name": "🥳 BHAI BHEN HOT 🥳", "price": "89", "validity": "365 Days"},
    "p6": {"name": "🥵 HOT DESI BHABHI 6 🥵", "price": "111", "validity": "60 Days"},
    "p7": {"name": "😳 INFLUENCER 50%-OFF 7 🥵", "price": "129", "validity": "60 Days"},
    "p8": {"name": "🔞 PAID PACK 🔞", "price": "88", "validity": "30 Days"},
    "p10": {"name": "😍 VVIP PLAN 1 LAKH VIDEO 😍", "price": "277", "validity": "365 Days"}
}

def send_section_details(chat_id, key):
    sec = sections[key]
    preview_folder = f"previews/{key}"
    album = []
    if os.path.exists(preview_folder):
        files = sorted(os.listdir(preview_folder))
        for f in files:
            full_path = os.path.join(preview_folder, f)
            obj = get_media_object(full_path)
            if obj:
                album.append(obj)

    if len(album) > 0:
        try:
            bot.send_media_group(chat_id, album)
        except Exception as e:
            logging.error(f"Section Media Group Error: {e}")

    caption = f"✨ **Plan Selected:** {sec['name']}\n\n💰 Price: **₹{sec['price']}**\n⏳ Validity: **{sec['validity']}**\n\nClick Buy Now to continue."
    bot.send_message(chat_id, caption, reply_markup=get_product_buy_keyboard(key))

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
        logging.error(f"Send photo error: {e}")
        bot.send_message(chat_id, payment_caption, reply_markup=get_payment_action_keyboard(txn_id))

# ---------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "User"
    add_user(message.chat.id, username, first_name)
    send_start_sequence(message.chat.id, first_name)

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    admin_states[ADMIN_ID] = "WAITING_BROADCAST"
    bot.send_message(ADMIN_ID, "📢 Send the message/photo you want to broadcast to all users:")

@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_all_messages(message):
    chat_id = message.chat.id

    if chat_id == ADMIN_ID and admin_states.get(ADMIN_ID) == "WAITING_BROADCAST":
        admin_states.pop(ADMIN_ID, None)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        conn.close()

        count = 0
        for u in users:
            try:
                bot.copy_message(u[0], chat_id, message.message_id)
                count += 1
            except:
                pass
        bot.send_message(ADMIN_ID, f"📢 Broadcast successfully sent to {count} users!")
        return

    if chat_id == ADMIN_ID and ADMIN_ID in admin_states:
        state = admin_states.pop(ADMIN_ID, None)
        if state.startswith("WAITING_LINK_"):
            parts = state.split("_")
            target_user_id = int(parts[2])
            txn_id = parts[3]

            vip_link = message.text.strip()
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE transactions SET status='APPROVED' WHERE txn_id=?", (txn_id,))
            conn.commit()
            conn.close()

            bot.send_message(target_user_id, f"🎉 **PAYMENT CONFIRMED!**\n\nYour VIP Link:\n{vip_link}")
            bot.send_message(ADMIN_ID, f"✅ Verified & Link sent to user `{target_user_id}`!")

# ---------------------------------------------------------
# CALLBACK QUERY HANDLER
# ---------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data in sections:
        send_section_details(chat_id, data)

    elif data.startswith("buy_"):
        plan_id = data.split("_")[1]
        username = call.from_user.username or "No Username"
        if plan_id in sections:
            send_payment_qr(chat_id, sections[plan_id], username)

    elif data.startswith("chkpay_"):
        txn_id = data.split("_")[1]
        bot.send_message(chat_id, "⏳ Request sent to Admin for verification!")

        bot.send_message(
            ADMIN_ID, 
            f"🔔 **New Verification Request!**\n\nUser ID: `{chat_id}`\nTxn ID: `{txn_id}`",
            reply_markup=get_admin_approval_keyboard(chat_id, txn_id)
        )

    elif data.startswith("adm_approve_"):
        parts = data.split("_")
        user_id = parts[2]
        txn_id = parts[3]

        admin_states[ADMIN_ID] = f"WAITING_LINK_{user_id}_{txn_id}"
        bot.send_message(ADMIN_ID, f"🔗 Paste/Send VIP Link for Txn ID `{txn_id}`:")

    elif data.startswith("adm_reject_"):
        parts = data.split("_")
        user_id = int(parts[2])
        txn_id = parts[3]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE transactions SET status='REJECTED' WHERE txn_id=?", (txn_id,))
        conn.commit()
        conn.close()

        bot.send_message(user_id, f"❌ **Payment Rejected!** Txn ID `{txn_id}` verify nahi hua.")
        bot.send_message(ADMIN_ID, f"🚫 Rejected Txn `{txn_id}`.")

    elif data == "back":
        send_start_sequence(chat_id, call.from_user.first_name or "User")

if __name__ == '__main__':
    keep_alive()
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(non_stop=True)
def get_media_object(f_path):
    if os.path.exists(f_path):
        if f_path.endswith(('.mp4', '.mkv', '.mov')):
            return InputMediaVideo(open(f_path, 'rb'), supports_streaming=True)
        elif f_path.endswith(('.jpg', '.jpeg', '.png')):
            return InputMediaPhoto(open(f_path, 'rb'))
    return None

# ---------------------------------------------------------
# START SEQUENCE & SECTION SENDER
# ---------------------------------------------------------
def send_start_sequence(chat_id, user_name):
    start_files = [
        "videos/video1.mp4",
        "videos/photo1.jpg",
        "videos/video2.mp4",
        "videos/video3.mp4",
        "videos/video4.mp4"
    ]
    
    album = []
    for f in start_files:
        obj = get_media_object(f)
        if obj:
            album.append(obj)

    if len(album) > 0:
        try:
            bot.send_media_group(chat_id, album)
        except Exception as e:
            logging.error(f"Start Media Group Error: {e}")

    quality_text = "✨ **TRY OUR ANY PLAN FOR CHECKING THE QUALITY** ✨"
    bot.send_message(chat_id, quality_text)
    
    welcome_msg = f"👋 Hello, 🦋💸**{user_name}**!\n\nChoose a plan to get started:"
    bot.send_message(chat_id, welcome_msg, reply_markup=get_main_keyboard())

def send_section_content(chat_id, plan_id, plan_title, price, validity, desc, media_files):
    
    caption_text = (
        f"{desc}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **{plan_title}**\n"
        f"💎 **Price:** `₹{price}` | ⏱️ **Validity:** `{validity}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👉 *Tap 'Buy Now' below to complete payment & unlock instant access!*"
    )

    valid_media = []
    for f_path in media_files:
        obj = get_media_object(f_path)
        if obj:
            valid_media.append(obj)

    if len(valid_media) > 1:
        try:
            bot.send_media_group(chat_id, valid_media)
        except Exception as e:
            logging.error(f"Media group error: {e}")
        bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard(plan_id))

    elif len(valid_media) == 1:
        single_path = media_files[0]
        try:
            if single_path.endswith(('.mp4', '.mkv', '.mov')):
                with open(single_path, 'rb') as v:
                    bot.send_video(
                        chat_id, v, 
                        caption=caption_text, 
                        supports_streaming=True, 
                        reply_markup=get_product_buy_keyboard(plan_id)
                    )
            else:
                with open(single_path, 'rb') as p:
                    bot.send_photo(
                        chat_id, p, 
                        caption=caption_text, 
                        reply_markup=get_product_buy_keyboard(plan_id)
                    )
        except Exception as e:
            logging.error(f"Single media send error: {e}")
            bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard(plan_id))

    else:
        bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard(plan_id))
        # ---------------------------------------------------------
# DYNAMIC PAYMENT QR SCREEN
# ---------------------------------------------------------
def send_payment_qr(chat_id, plan_info):
    txn_id = str(random.randint(100000000000000, 999999999999999))
    plan_name = plan_info["name"]
    amount = plan_info["price"]
    validity = plan_info["validity"]

    pending_verifications[txn_id] = {
        "user_id": chat_id,
        "plan": plan_name,
        "amount": amount,
        "validity": validity
    }

    encoded_name = urllib.parse.quote(MY_UPI_NAME)
    upi_url = f"upi://pay?pa={MY_UPI_ID}&pn={encoded_name}&am={amount}&cu=INR"
    qr_code_api = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={urllib.parse.quote(upi_url)}"

    payment_caption = (
        f"💳 **Scan & Pay**\n\n"
        f"📦 Plan: **{plan_name}**\n"
        f"💰 Amount: **₹{amount}.00**\n"
        f"⏳ Validity: **{validity}**\n\n"
        f"🧾 Transaction ID:\n`{txn_id}`\n\n"
        f"📲 **Scan the QR above** with any UPI app — the exact amount **₹{amount}.00** is filled in automatically.\n\n"
        f"✅ After paying, tap **Check Payment Status** — your plan unlocks instantly once the payment is confirmed."
    )

    try:
        bot.send_photo(
            chat_id, 
            photo=qr_code_api, 
            caption=payment_caption, 
            reply_markup=get_payment_action_keyboard(txn_id)
        )
    except Exception as e:
        logging.error(f"QR Send Error: {e}")
        bot.send_message(
            chat_id, 
            payment_caption, 
            reply_markup=get_payment_action_keyboard(txn_id)
        )

# ---------------------------------------------------------
# UNIQUE PLAN DETAILS
# ---------------------------------------------------------
sections = {
    "p1": {
        "name": "💦 𝐑𝐞𝐚𝐥 𝐈𝐧𝐝!𝐚𝐧 𝐃ē𝐬𝐢 𝐏𝟎𝐫𝐧 🫦", 
        "price": "69", 
        "validity": "30 Days",
        "desc": (
            "🔥 **ULTIMATE DESI COLLECTION** 🔥\n\n"
            "✨ *40,000+ Full HD Indian Videos*\n"
            "⚡ *Daily New Viral Releases*\n"
            "🔒 *Instant Private Group Access*"
        ),
        "media": ["videos/video1.mp4", "videos/video2.mp4"] 
    },
    "p2": {
        "name": "🌽 𝐇𝐎𝐓 𝐃𝐄𝐒𝐈 𝐕𝐈𝐏 𝐏𝐀𝐂𝐊 🌽", 
        "price": "79", 
        "validity": "30 Days",
        "desc": (
            "⚡ **SPECIAL PREMIUM STARTER** ⚡\n\n"
            "🎯 *50,000+ Trending Videos*\n"
            "🎬 *High Speed Cloud Server Streaming*\n"
            "✨ *Exclusive Leaked Collection*"
        ),
        "media": ["videos/video3.mp4", "videos/photo2.jpg"]
    },
    "p3": {
        "name": "✨ 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐗𝐂𝐋𝐔𝐒𝐈𝐕𝐄 𝐕𝐈𝐏 ✨", 
        "price": "96", 
        "validity": "30 Days",
        "desc": (
            "👑 **ROYAL ACCESS PASS** 👑\n\n"
            "🌟 *100,000+ Ultra HD Media Files*\n"
            "🚀 *Uncensored Daily Stream*\n"
            "🛡️ *Permanent Access Backup Links*"
        ),
        "media": ["videos/video4.mp4", "videos/video5.mp4", "videos/video6.mp4"]
    },
    "p4": {
        "name": "🎁 𝐒𝐏𝐄𝐂𝐈𝐀🇱 𝐃𝐈𝐒𝐂𝐎𝐔𝐍𝐓 𝐎𝐅𝐅𝐄𝐑 🎁", 
        "price": "155", 
        "validity": "30 Days",
        "desc": (
            "💥 **MEGA DISCOUNT COMBO** 💥\n\n"
            "🎉 *All 5 VIP Channels Access*\n"
            "💎 *Full Vault Unlock (Archive Content)*\n"
            "⚡ *Zero Compression Original Quality*"
        ),
        "media": ["videos/video7.mp4", "videos/video8.mp4", "videos/photo3.jpg"]
    },
    "p5": {
        "name": "🥳 𝟏-𝐘𝐄𝐀𝐑 𝐔𝐍𝐋𝐈𝐌𝐈𝐓𝐄𝐃 𝐏𝐀𝐒𝐒 🥳", 
        "price": "89", 
        "validity": "365 Days",
        "desc": (
            "🌟 **BEST VALUE YEARLY SAVER** 🌟\n\n"
            "⏳ *365 Days Full Unlimited Streaming*\n"
            "🔓 *No Monthly Renewal Needed*\n"
            "🚀 *VIP Fast Track Server Access*"
        ),
        "media": ["videos/photo4.jpg", "videos/photo5.jpg", "videos/video1.mp4"]
    },
    "p6": {
        "name": "🥵 𝟔𝟎 𝐃𝐀𝐘𝐒 𝐌𝐄𝐆𝐀 𝐕𝐈𝐏 🥵", 
        "price": "111", 
        "validity": "60 Days",
        "desc": (
            "🔥 **DOUBLE MONTH SUPER PACK** 🔥\n\n"
            "📍 *2 Months Non-Stop Premium Updates*\n"
            "🍿 *Exclusive Short Clips & Full Movies*\n"
            "⚡ *Instant Auto-Approval Access*"
        ),
        "media": ["videos/video2.mp4", "videos/video3.mp4", "videos/photo6.jpg"]
    },
    "p7": {
        "name": "😳 𝐈𝐍𝐅𝐋𝐔𝐄𝐍𝐂𝐄𝐑 𝟓𝟎% 𝐎𝐅𝐅 🥵", 
        "price": "129", 
        "validity": "60 Days",
        "desc": (
            "⭐ **INFLUENCER SPECIAL VAULT** ⭐\n\n"
            "📈 *Top Rated Viral Videos Collection*\n"
            "🎯 *50% Limited Time Offer*\n"
            "💎 *Direct Private Channel Invitation*"
        ),
        "media": ["videos/video4.mp4", "videos/video5.mp4", "videos/video6.mp4"]
    },
    "p8": {
        "name": "🔞 𝐏𝐀𝐈𝐃 𝐕𝐈𝐏 𝐒𝐏𝐄𝐂𝐈𝐀𝐋 🔞", 
        "price": "88", 
        "validity": "30 Days",
        "desc": (
            "⚡ **TOP SECRET ACCESS PACK** ⚡\n\n"
            "🔮 *Rare Unreleased Videos*\n"
            "🔒 *Private Server High Speed Streaming*\n"
            "💫 *Lifetime Chat Support Included*"
        ),
        "media": ["videos/video7.mp4", "videos/video8.mp4", "videos/video1.mp4"]
    },
    "p10": {
        "name": "🔴 𝟏𝟎-𝐆𝐑𝐎𝐔𝐏 𝐌𝐄𝐆𝐀 𝐁𝐔𝐍𝐃𝐋𝐄 🔴", 
        "price": "277", 
        "validity": "365 Days",
        "desc": (
            "👑 **THE ULTIMATE VIP MASTER PASS** 👑\n\n"
            "🚀 *Get Links To 10 All-in-One Premium Groups*\n"
            "💎 *Lifetime Permanent Membership*\n"
            "🎉 *All Viral, Exclusive & Original Media*"
        ),
        "media": ["videos/photo5.jpg", "videos/photo6.jpg", "videos/photo7.jpg"]
    }
}

# ---------------------------------------------------------
# HANDLERS & CALLBACKS
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    send_start_sequence(message.chat.id, user_name)

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Admin only command!")
        return

    msg = bot.reply_to(message, "📢 Broadcast message send karein:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    count = 0
    for u_id in users_list:
        try:
            bot.copy_message(chat_id=u_id, from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data in sections:
        sec = sections[data]
        send_section_content(
            chat_id,
            data,
            sec["name"], 
            sec["price"], 
            sec["validity"], 
            sec["desc"], 
            sec["media"]
        )

    elif data.startswith("buy_"):
        plan_id = data.split("_")[1]
        if plan_id in sections:
            send_payment_qr(chat_id, sections[plan_id])

    elif data.startswith("chkpay_"):
        txn_id = data.split("_")[1]
        user_id = call.from_user.id
        user_name = call.from_user.first_name
        username = f"@{call.from_user.username}" if call.from_user.username else "No Username"
        
        info = pending_verifications.get(txn_id, {"plan": "VVIP Plan", "amount": "N/A"})

        admin_alert = (
            f"🚨 **NEW PAYMENT VERIFICATION REQUEST!**\n\n"
            f"👤 **User:** {user_name} ({username})\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"📦 **Plan:** {info['plan']}\n"
            f"💰 **Amount:** ₹{info['amount']}\n"
            f"🧾 **Txn ID:** `{txn_id}`\n\n"
            f"👇 Click below button to Approve or Cancel:"
        )
        try:
            bot.send_message(
                ADMIN_ID, 
                admin_alert, 
                reply_markup=get_admin_approval_keyboard(user_id, txn_id)
            )
        except Exception as e:
            logging.error(f"Admin Alert Error: {e}")

        bot.send_message(
            chat_id, 
            "⏳ **Checking Payment Status...**\n\nAapki payment details Admin ko verify karne ke liye bhej di gayi hai. Direct approve hote hi aapko link mil jayega!",
            reply_markup=get_product_buy_keyboard("p1")
        )

    elif data.startswith("adm_approve_"):
        if call.from_user.id != ADMIN_ID:
            bot.send_message(chat_id, "⚠️ Only Admin can use these buttons!")
            return

        parts = data.split("_")
        target_user_id = int(parts[2])
        txn_id = parts[3]

        msg = bot.send_message(ADMIN_ID, f"✅ Enter Private VIP Link/Access for User ID `{target_user_id}` (Txn: {txn_id}):")
        bot.register_next_step_handler(msg, process_admin_vip_link, target_user_id, txn_id, call.message.message_id)

    elif data.startswith("adm_reject_"):
        if call.from_user.id != ADMIN_ID:
            bot.send_message(chat_id, "⚠️ Only Admin can use these buttons!")
            return

        parts = data.split("_")
        target_user_id = int(parts[2])
        txn_id = parts[3]

        try:
            bot.send_message(
                target_user_id, 
                f"❌ **Payment Status: REJECTED / FAILED**\n\nAapki payment ID (`{txn_id}`) verify nahi ho payi. Agar aapne payment kar di hai to Screenshot ke sath Admin se contact karein: @{ADMIN_USERNAME}"
            )
            bot.edit_message_text(
                f"❌ **Payment Rejected/Cancelled for User ID `{target_user_id}` (Txn: {txn_id})**", 
                ADMIN_ID, 
                call.message.message_id
            )
        except Exception as e:
            logging.error(f"Reject send error: {e}")

    elif data == "how_to_use":
        how_to_text = "📖 **How to Use Guide**\n\n1. Select any plan.\n2. Scan QR Code & pay exact amount.\n3. Click 'Check Payment Status'."
        bot.send_message(chat_id, how_to_text, reply_markup=get_product_buy_keyboard("p1"))

    elif data == "report_issue":
        report_text = "📝 **Apni complaint / payment screenshot yahan bhejien:**"
        msg = bot.send_message(chat_id, report_text)
        bot.register_next_step_handler(msg, process_user_complaint)

    elif data == "back":
        user_name = call.from_user.first_name
        send_start_sequence(chat_id, user_name)

def process_admin_vip_link(message, target_user_id, txn_id, admin_msg_id):
    vip_link = message.text.strip()
    
    success_msg = (
        f"🎉 **PAYMENT VERIFIED & CONFIRMED!** 🎉\n\n"
        f"Aapka payment successful confirm ho gaya hai.\n\n"
        f"🔗 **Your VIP Link / Access:**\n{vip_link}\n\n"
        f"Enjoy your VIP Content! 💥"
    )

    try:
        bot.send_message(target_user_id, success_msg)
        bot.send_message(ADMIN_ID, f"✅ **VIP Access Link successfully sent to User ID `{target_user_id}`!**")
        
        bot.edit_message_text(
            f"✅ **Payment Verified & Link Sent for User ID `{target_user_id}` (Txn: {txn_id})**", 
            ADMIN_ID, 
            admin_msg_id
        )
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error sending link to user: {e}")

def process_user_complaint(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    admin_notification = (
        f"🚨 **NEW USER COMPLAINT / SCREENSHOT RECEIVED!**\n\n"
        f"👤 **User:** {user_name} ({username})\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"----------------------------------"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_notification)
        bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "✅ **Apka message Admin ko bhej diya gaya hai!**", reply_markup=get_product_buy_keyboard("p1"))
    except Exception as e:
        logging.error(f"Complaint Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Complaint error. Direct Admin se contact karein.", reply_markup=get_product_buy_keyboard("p1"))

# ---------------------------------------------------------
# BOT STARTUP & RECONNECT LOOP
# ---------------------------------------------------------
if __name__ == '__main__':
    keep_alive()
    
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
    except Exception as e:
        logging.warning(f"Could not clear webhooks: {e}")

    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Polling crash prevented: {e}")
            time.sleep(3)
