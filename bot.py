import os
import logging
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

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

# Side-Menu Bar Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    print(f"Commands set error: {e}")

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

def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back")
    btn_buy = InlineKeyboardButton("💬 Buy / Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn_back)
    markup.add(btn_buy)
    return markup

# ---------------------------------------------------------
# MEDIA SENDER HELPER FUNCTION
# ---------------------------------------------------------
def send_media_or_text(chat_id, text, file_path, reply_markup):
    """Local file upload karta hai agar file folder me maujood ho"""
    if os.path.exists(file_path):
        try:
            if file_path.endswith(('.mp4', '.mkv', '.mov')):
                with open(file_path, 'rb') as video:
                    bot.send_video(chat_id, video, caption=text, reply_markup=reply_markup)
                return
            elif file_path.endswith(('.jpg', '.jpeg', '.png')):
                with open(file_path, 'rb') as photo:
                    bot.send_photo(chat_id, photo, caption=text, reply_markup=reply_markup)
                return
        except Exception as e:
            print(f"Error sending file {file_path}: {e}")
            
    # Agar file nahi milti ya fail hoti hai to simple message bhejega
    bot.send_message(chat_id, text, reply_markup=reply_markup)

# ---------------------------------------------------------
# BOT HANDLERS
# ---------------------------------------------------------

@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    welcome_text = f"👋 Hello, {user_name}!\n\nChoose a plan to get started:"
    
    # Start hone par videos/video1.mp4 bhejega
    send_media_or_text(message.chat.id, welcome_text, "videos/video1.mp4", get_main_keyboard())

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "📢 Broadcast ke liye text/media reply karein:")
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

    # Plans Details mapped with respective repo files (videos/ & photos/)
    plans_config = {
        "p1": {"text": "💎 **PLAN 1 Details**\n\nPrice: ₹69\nValidity: 30 Days", "file": "videos/video2.mp4"},
        "p2": {"text": "💎 **PLAN 2 Details**\n\nPrice: ₹79\nValidity: 30 Days", "file": "videos/video3.mp4"},
        "p3": {"text": "💎 **PLAN 3 Details**\n\nPrice: ₹96\nValidity: 30 Days", "file": "videos/video4.mp4"},
        "p4": {"text": "✨ **OFFER PLAN Details**\n\nPrice: ₹155\nValidity: 30 Days", "file": "videos/video5.mp4"},
        "p5": {"text": "🥳 **BEST OFFER PLAN Details**\n\nPrice: ₹89\nValidity: 365 Days", "file": "videos/video6.mp4"},
        "p6": {"text": "💎 **PLAN 6 Details**\n\nPrice: ₹111\nValidity: 60 Days", "file": "videos/photo1.jpg"},
        "p7": {"text": "💎 **PLAN 7 Details**\n\nPrice: ₹129\nValidity: 60 Days", "file": "videos/photo2.jpg"},
        "p8": {"text": "💎 **PAID PACK Details**\n\nPrice: ₹88\nValidity: 30 Days", "file": "videos/photo3.jpg"},
        "p9": {"text": "💎 **VIP VIDEO PACK Details**\n\nPrice: ₹277\nValidity: 365 Days", "file": "videos/photo4.jpg"},
        "how_to_use": {"text": "📖 **How to Use Guide**\n\n1. Plan choose karein.\n2. Access lene ke liye Admin contact karein ya Issue Report karein.", "file": "videos/photo5.jpg"}
    }

    if data in plans_config:
        info = plans_config[data]
        send_media_or_text(chat_id, info["text"], info["file"], get_back_keyboard())

    elif data == "report_issue":
        msg = bot.send_message(chat_id, "📝 **Apni complaint / issue yahan type karke bhejien:**\n\n(Aap photo, video ya text bhej sakte hain)")
        bot.register_next_step_handler(msg, process_user_complaint)

    elif data == "back":
        user_name = call.from_user.first_name
        welcome_text = f"👋 Hello, {user_name}!\n\nChoose a plan to get started:"
        send_media_or_text(chat_id, welcome_text, "videos/video1.mp4", get_main_keyboard())

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
        # Step 1: Send Header Info to Admin
        bot.send_message(ADMIN_ID, admin_notification)
        # Step 2: Forward exact media/photo/video/text to Admin
        bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        # Step 3: Send Confirmation to User
        bot.send_message(message.chat.id, "✅ **Aapki complaint Admin ko bhej di gayi hai!**\nJald hi aapko response mil jayega.", reply_markup=get_back_keyboard())
    except Exception as e:
        print(f"Complaint Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Complaint bhejne mein error aaya. Kripya Admin se direct chat karein.", reply_markup=get_back_keyboard())

# ---------------------------------------------------------
# BOT STARTUP
# ---------------------------------------------------------
if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
