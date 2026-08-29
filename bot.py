import os
import time
import logging
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
    return "Bot Online & Running!"

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
# BOT CONFIGURATION
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "kushal_owner")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
users_list = set()

# Setup Commands
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    logging.error(f"Commands setup error: {e}")

# ---------------------------------------------------------
# KEYBOARD LAYOUTS
# ---------------------------------------------------------
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        InlineKeyboardButton("PLAN 1 — ₹69 / 30d", callback_data="p1"),
        InlineKeyboardButton("PLAN 2 — ₹79 / 30d", callback_data="p2"),
        InlineKeyboardButton("PLAN 3 — ₹96 / 30d", callback_data="p3"),
        InlineKeyboardButton("OFFER ✨ — ₹155 / 30d", callback_data="p4"),
        InlineKeyboardButton("BEST OFFER 🥳 — ₹89 / 365d", callback_data="p5"),
        InlineKeyboardButton("PLAN 6 — ₹111 / 60d", callback_data="p6"),
        InlineKeyboardButton("PLAN 7 — ₹129 / 60d", callback_data="p7"),
        InlineKeyboardButton("PAID PACK — ₹88 / 30d", callback_data="p8"),
        InlineKeyboardButton("PLAN 9 — ₹111 / 60d", callback_data="p9"),
        InlineKeyboardButton("VIP VIDEO — ₹277 / 365d", callback_data="p10")
    )
    
    markup.row(
        InlineKeyboardButton("📖 How to Use", callback_data="how_to_use"),
        InlineKeyboardButton("🚨 Report Issue", callback_data="report_issue")
    )
    return markup

def get_product_buy_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 Buy Now", url=f"https://t.me/{ADMIN_USERNAME}"),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    )
    return markup

# ---------------------------------------------------------
# FAST DYNAMIC MEDIA SENDER
# ---------------------------------------------------------
def send_section_content(chat_id, plan_title, price, validity, desc, media_files):
    caption_text = (
        f"{desc}\n\n"
        f"📦 **{plan_title}** 😍\n"
        f"💰 **Price: ₹{price}** | ⏳ **{validity}**"
    )

    valid_media = []
    for f_path in media_files:
        if os.path.exists(f_path):
            if f_path.endswith(('.mp4', '.mkv', '.mov')):
                valid_media.append(InputMediaVideo(open(f_path, 'rb'), supports_streaming=True))
            elif f_path.endswith(('.jpg', '.jpeg', '.png')):
                valid_media.append(InputMediaPhoto(open(f_path, 'rb')))

    if len(valid_media) > 1:
        try:
            bot.send_media_group(chat_id, valid_media)
        except Exception as e:
            logging.error(f"Media group send error: {e}")
        bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard())

    elif len(valid_media) == 1:
        single_path = media_files[0]
        try:
            if single_path.endswith(('.mp4', '.mkv', '.mov')):
                with open(single_path, 'rb') as v:
                    bot.send_video(
                        chat_id, v, 
                        caption=caption_text, 
                        supports_streaming=True, 
                        reply_markup=get_product_buy_keyboard()
                    )
            else:
                with open(single_path, 'rb') as p:
                    bot.send_photo(
                        chat_id, p, 
                        caption=caption_text, 
                        reply_markup=get_product_buy_keyboard()
                    )
        except Exception as e:
            logging.error(f"Single media send error: {e}")
            bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard())

    else:
        bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard())

# ---------------------------------------------------------
# HANDLERS
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    welcome_text = f"👋 Hello, **{user_name}**!\n\nChoose a plan from below to get started:"
    
    if os.path.exists("videos/video1.mp4"):
        with open("videos/video1.mp4", "rb") as vid:
            bot.send_video(message.chat.id, vid, caption=welcome_text, supports_streaming=True, reply_markup=get_main_keyboard())
    else:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

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

    sections = {
        "p1": {
            "name": "PLAN 1 PACK", "price": "69", "validity": "30 Days",
            "desc": "PERMANENT VVIP GROUP ACCESS",
            "media": ["videos/video1.mp4", "videos/video2.mp4"] 
        },
        "p2": {
            "name": "PLAN 2 PACK", "price": "79", "validity": "30 Days",
            "desc": "HOT DESI VVIP PACK",
            "media": ["videos/photo1.jpg", "videos/video2.mp4"]
        },
        "p3": {
            "name": "PLAN 3 PACK", "price": "96", "validity": "30 Days",
            "desc": "PREMIUM EXCLUSIVE ACCESS",
            "media": ["videos/video1.mp4", "videos/video2.mp4", "videos/video3.mp4"]
        },
        "p4": {
            "name": "OFFER PACK ✨", "price": "155", "validity": "30 Days",
            "desc": "SPECIAL DISCOUNT OFFER WITH FULL MEDIA",
            "media": ["videos/video4.mp4", "videos/video1.mp4", "videos/video2.mp4"]
        },
        "p5": {
            "name": "BEST OFFER 🥳", "price": "89", "validity": "365 Days",
            "desc": "1 YEAR UNLIMITED VIP ACCESS",
            "media": ["videos/video5.mp4", "videos/video1.mp4", "videos/video3.mp4"]
        },
        "p6": {
            "name": "PLAN 6 PACK", "price": "111", "validity": "60 Days",
            "desc": "60 DAYS FULL VVIP PACK",
            "media": ["videos/photo2.jpg", "videos/video6.mp4", "videos/video2.mp4"]
        },
        "p7": {
            "name": "PLAN 7 PACK", "price": "129", "validity": "60 Days",
            "desc": "INFLUENCER 50% OFF PACK",
            "media": ["videos/video7.mp4", "videos/video1.mp4", "videos/video3.mp4"]
        },
        "p8": {
            "name": "PAID PACK", "price": "88", "validity": "30 Days",
            "desc": "BAAP BETI VVIP SPECIAL PACK",
            "media": ["videos/video8.mp4", "videos/video2.mp4", "videos/video3.mp4"]
        },
        "p9": {
            "name": "PLAN 9 PACK", "price": "111", "validity": "60 Days",
            "desc": "SUPER VIP ACCESS PACK",
            "media": ["videos/video9.mp4", "videos/video1.mp4", "videos/video2.mp4"]
        },
        "p10": {
            "name": "VVIP PLAN 1 LAKH VIDEO", "price": "277", "validity": "365 Days",
            "desc": "PERMANENT VVIP GROUP YOU WILL GET 10 GROUP LINKS ALL VIRAL AND PREMIUM GROUP WORTH IT JUST BUY 🥵💦",
            "media": ["videos/video1.mp4", "videos/video2.mp4", "videos/video3.mp4"]
        }
    }

    if data in sections:
        sec = sections[data]
        send_section_content(
            chat_id, 
            sec["name"], 
            sec["price"], 
            sec["validity"], 
            sec["desc"], 
            sec["media"]
        )

    elif data == "how_to_use":
        bot.send_message(
            chat_id, 
            "📖 **How to Use Guide**\n\n1. Select any plan.\n2. Click '💳 Buy Now' to contact Admin.", 
            reply_markup=get_product_buy_keyboard()
        )

    elif data == "report_issue":
        msg = bot.send_message(chat_id, "📝 **Apni complaint yahan bhejien (Text/Photo/Video):**")
        bot.register_next_step_handler(msg, process_user_complaint)

    elif data == "back":
        user_name = call.from_user.first_name
        welcome_text = f"👋 Hello, **{user_name}**!\n\nChoose a plan from below to get started:"
        if os.path.exists("videos/video1.mp4"):
            with open("videos/video1.mp4", "rb") as vid:
                bot.send_video(chat_id, vid, caption=welcome_text, supports_streaming=True, reply_markup=get_main_keyboard())
        else:
            bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard())

def process_user_complaint(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    admin_notification = (
        f"🚨 **NEW USER COMPLAINT RECEIVED!**\n\n"
        f"👤 **User:** {user_name} ({username})\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"----------------------------------"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_notification)
        bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "✅ **Aapki complaint Admin ko bhej di gayi hai!**", reply_markup=get_product_buy_keyboard())
    except Exception as e:
        logging.error(f"Complaint Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Complaint error. Direct Admin se contact karein.", reply_markup=get_product_buy_keyboard())

# ---------------------------------------------------------
# SAFE BOT STARTUP & RECONNECT LOOP
# ---------------------------------------------------------
if __name__ == '__main__':
    keep_alive()
    
    # Safe Reset Webhook & Clear Pending Updates
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
    except Exception as e:
        logging.warning(f"Could not clear webhooks: {e}")

    # Auto Reconnect Polling Loop
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Polling crash prevented: {e}")
            time.sleep(3)
