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

# Media Files Path / File IDs (Aap yahan direct URL, File ID ya local file path de sakte hain)
START_PHOTO = os.environ.get("START_PHOTO", "https://picsum.photos/800/400") # Direct URL / Local Path / File ID
START_VIDEO = os.environ.get("START_VIDEO", "") # Telegram Video File_ID ya local video path (Optional)

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
    
    # Bottom Row: 'How to Use' + Direct Bot Complaint Button
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
# SAFE MEDIA SENDER HELPER
# ---------------------------------------------------------
def send_welcome_media_and_text(chat_id, user_name):
    welcome_text = (
        f"👋 Hello, {user_name}!\n\n"
        f"Choose a plan to get started:"
    )

    # 1. Send Photo (Agar Available ho)
    if START_PHOTO:
        try:
            bot.send_photo(chat_id, START_PHOTO)
        except Exception as e:
            print(f"Photo send error: {e}")

    # 2. Send Video (Agar Available ho)
    if START_VIDEO:
        try:
            bot.send_video(chat_id, START_VIDEO)
        except Exception as e:
            print(f"Video send error: {e}")

    # 3. Send Text + Main Buttons Menu
    bot.send_message(
        chat_id, 
        welcome_text, 
        reply_markup=get_main_keyboard()
    )

# ---------------------------------------------------------
# BOT HANDLERS
# ---------------------------------------------------------

# /start Command Handler
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    send_welcome_media_and_text(message.chat.id, user_name)

# /broadcast Command Handler (Admin Only)
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

# Callback Buttons Handling
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    plans_info = {
        "p1": "💎 **PLAN 1 Details**\n\nPrice: ₹69\nValidity: 30 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p2": "💎 **PLAN 2 Details**\n\nPrice: ₹79\nValidity: 30 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p3": "💎 **PLAN 3 Details**\n\nPrice: ₹96\nValidity: 30 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p4": "✨ **OFFER PLAN Details**\n\nPrice: ₹155\nValidity: 30 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p5": "🥳 **BEST OFFER PLAN Details**\n\nPrice: ₹89\nValidity: 365 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p6": "💎 **PLAN 6 Details**\n\nPrice: ₹111\nValidity: 60 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p7": "💎 **PLAN 7 Details**\n\nPrice: ₹129\nValidity: 60 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p8": "💎 **PAID PACK Details**\n\nPrice: ₹88\nValidity: 30 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "p9": "💎 **VIP VIDEO PACK Details**\n\nPrice: ₹277\nValidity: 365 Days\n\nIs plan ko buy karne ke liye Admin button par click karein.",
        "how_to_use": "📖 **How to Use Guide**\n\n1. Plan choose karein.\n2. Access lene ke liye Admin contact karein ya Issue Report karein."
    }

    if data in plans_info:
        bot.send_message(chat_id, plans_info[data], reply_markup=get_back_keyboard())

    elif data == "report_issue":
        msg = bot.send_message(chat_id, "📝 **Apni complaint / issue yahan type karke bhejien:**\n\n(Aap photo, video ya text bhej sakte hain)")
        bot.register_next_step_handler(msg, process_user_complaint)

    elif data == "back":
        user_name = call.from_user.first_name
        send_welcome_media_and_text(chat_id, user_name)

# Direct Complaint Forwarder to Admin
def process_user_complaint(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    # Admin Alert Notification
    admin_notification = (
        f"🚨 **NEW USER COMPLAINT RECEIVED!**\n\n"
        f"👤 **User:** {user_name} ({username})\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"----------------------------------"
    )
    
    try:
        # Step 1: Send Notification Header to Admin
        bot.send_message(ADMIN_ID, admin_notification)
        
        # Step 2: Forward User's Exact Message/Media to Admin
        bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        
        # Step 3: Send Confirmation to User
        bot.send_message(message.chat.id, "✅ **Aapki complaint Admin ko bhej di gayi hai!**\nJald hi aapko response mil jayega.", reply_markup=get_back_keyboard())
    except Exception as e:
        print(f"Complaint Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Complaint bhejne mein error aaya. Kripya Admin se direct chat karein.", reply_markup=get_back_keyboard())

# ---------------------------------------------------------
# BOT STARTUP (Prevent Multi-Instance Collision)
# ---------------------------------------------------------
if __name__ == '__main__':
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
