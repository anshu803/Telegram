import os
import logging
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

logging.basicConfig(level=logging.INFO)

# Render Web Service & UptimeRobot Support
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Web Service Online"

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

# CONFIGURATION
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
# Apna Telegram Username Render me `ADMIN_USERNAME` me dalein (bina @ ke, e.g. "kushal_owner")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "kushal_owner")
ADMIN_ID = os.environ.get("ADMIN_ID", "123456789")

bot = telebot.TeleBot(BOT_TOKEN)
users_list = set()

# Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    print(f"Commands set error: {e}")

# Universal Main Menu (Sabhi Users Ke Liye Same Dynamic Layout)
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
    
    # Bottom Row: 'How to Use' + Dynamic 'Report Issue' Admin Redirect Link
    btn_how = InlineKeyboardButton("📖 How to Use", callback_data="how_to_use")
    btn_report = InlineKeyboardButton("🚨 Report Issue", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.row(btn_how, btn_report)
    return markup

def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    
    # Back to Menu Button + Direct Buy Contact Admin Button
    btn_back = InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back")
    btn_buy = InlineKeyboardButton("💬 Buy / Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn_back)
    markup.add(btn_buy)
    return markup

# /start Command Handler
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name

    welcome_text = (
        f"👋 Hello, {user_name}!\n\n"
        f"Choose a plan to get started:"
    )
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=get_main_keyboard()
    )

# /broadcast Command Handler (Sirf Real Admin Execute Kar Payega)
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "⚠️ Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "📢 Broadcast ke liye message send/reply karein:")
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

# Inline Buttons Callback Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    plans_info = {
        "p1": "💎 **PLAN 1 Details**\n\nPrice: ₹69\nValidity: 30 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p2": "💎 **PLAN 2 Details**\n\nPrice: ₹79\nValidity: 30 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p3": "💎 **PLAN 3 Details**\n\nPrice: ₹96\nValidity: 30 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p4": "✨ **OFFER PLAN Details**\n\nPrice: ₹155\nValidity: 30 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p5": "🥳 **BEST OFFER PLAN Details**\n\nPrice: ₹89\nValidity: 365 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p6": "💎 **PLAN 6 Details**\n\nPrice: ₹111\nValidity: 60 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p7": "💎 **PLAN 7 Details**\n\nPrice: ₹129\nValidity: 60 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p8": "💎 **PAID PACK Details**\n\nPrice: ₹88\nValidity: 30 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "p9": "💎 **VIP VIDEO PACK Details**\n\nPrice: ₹277\nValidity: 365 Days\n\nIs plan ko buy karne ke liye neeche diye gaye Admin button par click karein.",
        "how_to_use": "📖 **How to Use Guide**\n\n1. Kisi bhi Plan Button par click karke details check karein.\n2. Buy karne ke liye 'Contact Admin' par click karke message karein."
    }

    if data in plans_info:
        bot.send_message(chat_id, plans_info[data], reply_markup=get_back_keyboard(), parse_mode="Markdown")
    
    elif data == "back":
        user_name = call.from_user.first_name
        msg = f"👋 Hello, {user_name}!\n\nChoose a plan to get started:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard())

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
