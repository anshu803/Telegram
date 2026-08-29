import os
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
# RENDER WEB SERVICE & UPTIMEROBOT SUPPORT
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Service Online & Running!"

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
    print(f"Commands error: {e}")

# ---------------------------------------------------------
# KEYBOARD LAYOUTS
# ---------------------------------------------------------
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton("PLAN 1 — ₹69 / 30d", callback_data="p1"))
    markup.add(InlineKeyboardButton("PLAN 2 — ₹79 / 30d", callback_data="p2"))
    markup.add(InlineKeyboardButton("PLAN 3 — ₹96 / 30d", callback_data="p3"))
    markup.add(InlineKeyboardButton("OFFER ✨ — ₹155 / 30d", callback_data="p4"))
    markup.add(InlineKeyboardButton("BEST OFFER 🥳 — ₹89 / 365d", callback_data="p5"))
    markup.add(InlineKeyboardButton("PLAN 6 — ₹111 / 60d", callback_data="p6"))
    markup.add(InlineKeyboardButton("PLAN 7 — ₹129 / 60d", callback_data="p7"))
    markup.add(InlineKeyboardButton("PAID PACK — ₹88 / 30d", callback_data="p8"))
    markup.add(InlineKeyboardButton("VIP VIDEO — ₹277 / 365d", callback_data="p9"))
    
    btn_how = InlineKeyboardButton("📖 How to Use", callback_data="how_to_use")
    btn_report = InlineKeyboardButton("🚨 Report Issue", callback_data="report_issue")
    markup.row(btn_how, btn_report)
    return markup

def get_product_buy_keyboard():
    markup = InlineKeyboardMarkup()
    btn_buy = InlineKeyboardButton("💳 Buy Now", url=f"https://t.me/{ADMIN_USERNAME}")
    btn_back = InlineKeyboardButton("⬅️ Back", callback_data="back")
    markup.add(btn_buy)
    markup.add(btn_back)
    return markup

# ---------------------------------------------------------
# HAR PRODUCT KE LIYE ALAG MEDIA ALBUM SENDER
# ---------------------------------------------------------
def send_product_details(chat_id, plan_title, price, validity, desc, video_list, photo_list):
    media = []
    
    # 1. Product specific Videos
    for v_path in video_list:
        if os.path.exists(v_path):
            media.append(InputMediaVideo(open(v_path, 'rb')))

    # 2. Product specific Photos
    for p_path in photo_list:
        if os.path.exists(p_path):
            media.append(InputMediaPhoto(open(p_path, 'rb')))

    # Caption (Bilkul aapke screenshot wale design par)
    caption_text = (
        f"{desc}\n\n"
        f"📦 **{plan_title}** 😍\n"
        f"💰 **Price: ₹{price}** | ⏳ **{validity}**"
    )

    # Step A: Album Media Grid Send Karo
    if media:
        try:
            bot.send_media_group(chat_id, media)
        except Exception as e:
            print(f"Media send error: {e}")

    # Step B: Direct Text + Buy Now / Back Buttons Send Karo
    bot.send_message(chat_id, caption_text, reply_markup=get_product_buy_keyboard())

# ---------------------------------------------------------
# BOT HANDLERS
# ---------------------------------------------------------

@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    welcome_text = f"👋 Hello, **{user_name}**!\n\nChoose a plan from below to get started:"
    
    if os.path.exists("videos/video1.mp4"):
        with open("videos/video1.mp4", "rb") as vid:
            bot.send_video(message.chat.id, vid, caption=welcome_text, reply_markup=get_main_keyboard())
    else:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "📢 Broadcast message/media send karein:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    count = 0
    for u_id in users_list:
        try:
            bot.copy_message(chat_id=u_id, from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast successfully {count} users ko bhej diya gaya!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # HAR BUTTON (PRODUCT) KA APNA ALAG SYSTEM CONFIGURATION
    products = {
        "p1": {
            "name": "PLAN 1 PACK", "price": "69", "validity": "30 Days",
            "desc": "PERMANENT VVIP GROUP YOU WILL GET ALL VIRAL AND PREMIUM CONTENT",
            "videos": ["videos/video1.mp4", "videos/video2.mp4"],
            "photos": ["videos/photo1.jpg"]
        },
        "p2": {
            "name": "PLAN 2 PACK", "price": "79", "validity": "30 Days",
            "desc": "FULL HD EXCLUSIVE MEDIA PACK",
            "videos": ["videos/video2.mp4", "videos/video3.mp4"],
            "photos": ["videos/photo2.jpg"]
        },
        "p3": {
            "name": "PLAN 3 PACK", "price": "96", "validity": "30 Days",
            "desc": "TOP TRENDING PREMIUM LINKS COLLECTION",
            "videos": ["videos/video3.mp4", "videos/video4.mp4"],
            "photos": ["videos/photo3.jpg"]
        },
        "p4": {
            "name": "OFFER PACK ✨", "price": "155", "validity": "30 Days",
            "desc": "SPECIAL DISCOUNT OFFER WITH EXTRA MEDIA ACCESS",
            "videos": ["videos/video4.mp4", "videos/video5.mp4"],
            "photos": ["videos/photo4.jpg"]
        },
        "p5": {
            "name": "BEST YEARLY OFFER 🥳", "price": "89", "validity": "365 Days",
            "desc": "1 YEAR FULL UNLIMITED ACCESS PACK",
            "videos": ["videos/video5.mp4", "videos/video6.mp4"],
            "photos": ["videos/photo5.jpg"]
        },
        "p6": {
            "name": "PLAN 6 PACK", "price": "111", "validity": "60 Days",
            "desc": "60 DAYS UNLIMITED VVIP LINKS",
            "videos": ["videos/video6.mp4", "videos/video7.mp4"],
            "photos": ["videos/photo6.jpg"]
        },
        "p7": {
            "name": "PLAN 7 PACK", "price": "129", "validity": "60 Days",
            "desc": "SUPER PREMIUM CONTENT PACK",
            "videos": ["videos/video7.mp4", "videos/video8.mp4"],
            "photos": ["videos/photo7.jpg"]
        },
        "p8": {
            "name": "PAID PACK", "price": "88", "validity": "30 Days",
            "desc": "EXCLUSIVE PAID VVIP GROUP LINKS",
            "videos": ["videos/video8.mp4", "videos/video9.mp4"],
            "photos": ["videos/photo1.jpg"]
        },
        "p9": {
            "name": "VVIP PLAN 1 LAKH VIDEO 🍿", "price": "277", "validity": "365 Days",
            "desc": "PERMANENT VVIP GROUP YOU WILL GET 10 GROUP LINKS ALL VIRAL AND PREMIUM GROUP WORTH IT JUST BUY 🥵💦",
            "videos": ["videos/video1.mp4", "videos/video2.mp4", "videos/video3.mp4"],
            "photos": ["videos/photo1.jpg", "videos/photo2.jpg", "videos/photo3.jpg"]
        }
    }

    if data in products:
        prod = products[data]
        send_product_details(
            chat_id, 
            prod["name"], 
            prod["price"], 
            prod["validity"], 
            prod["desc"], 
            prod["videos"], 
            prod["photos"]
        )

    elif data == "how_to_use":
        bot.send_message(
            chat_id, 
            "📖 **How to Use Guide**\n\n1. Kisi bhi plan par click karein.\n2. Screen par aae '💳 Buy Now' button par click karke Admin ko contact karein.", 
            reply_markup=get_product_buy_keyboard()
        )

    elif data == "report_issue":
        msg = bot.send_message(chat_id, "📝 **Apni complaint / issue yahan bhejien (Message/Photo/Video):**")
        bot.register_next_step_handler(msg, process_user_complaint)

    elif data == "back":
        user_name = call.from_user.first_name
        welcome_text = f"👋 Hello, **{user_name}**!\n\nChoose a plan from below to get started:"
        if os.path.exists("videos/video1.mp4"):
            with open("videos/video1.mp4", "rb") as vid:
                bot.send_video(chat_id, vid, caption=welcome_text, reply_markup=get_main_keyboard())
        else:
            bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard())

# Direct Complaint Forwarder to Admin
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
        print(f"Complaint Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Complaint nahi bhej sake. Admin se direct contact karein.", reply_markup=get_product_buy_keyboard())

# ---------------------------------------------------------
# BOT STARTUP
# ---------------------------------------------------------
if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
