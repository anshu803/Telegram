import os
import logging
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

logging.basicConfig(level=logging.INFO)

# Render Web Service / UptimeRobot Ping Setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Service Online"

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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN)
users_list = set()

# Side-Menu Bar Commands
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    print(f"Commands error: {e}")

# Main Keyboard Structure
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("VIP Movie Plan - ₹199", callback_data="b1"))
    markup.add(InlineKeyboardButton("Trading Signals - ₹499", callback_data="b2"))
    markup.add(InlineKeyboardButton("Premium Course - ₹299", callback_data="b3"))
    markup.add(InlineKeyboardButton("Pro Software Pack - ₹399", callback_data="b4"))
    markup.add(InlineKeyboardButton("Private Channel Access - ₹999", callback_data="b5"))
    markup.add(InlineKeyboardButton("Special Combo Offer - ₹599", callback_data="b6"))
    markup.add(InlineKeyboardButton("AI Tools Access - ₹349", callback_data="b7"))
    markup.add(InlineKeyboardButton("Referral Program - Free", callback_data="b8"))
    markup.add(InlineKeyboardButton("Lifetime Membership - ₹1499", callback_data="b9"))
    markup.add(InlineKeyboardButton("Exclusive VIP Pack - ₹1999", callback_data="b10"))
    
    # Bottom Row: Help (Left) & Admin (Right)
    btn_help = InlineKeyboardButton("Help", callback_data="help")
    btn_admin = InlineKeyboardButton("Admin", url=f"tg://user?id={ADMIN_ID}")
    markup.row(btn_help, btn_admin)
    return markup

def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="back"))
    return markup

# Safe Video Handler (Render storage full nahi hogi, fail hone par silent skip karega)
def try_send_video(chat_id, file_path_or_id):
    try:
        if os.path.exists(file_path_or_id):
            with open(file_path_or_id, 'rb') as f:
                bot.send_video(chat_id, f)
        elif isinstance(file_path_or_id, str) and len(file_path_or_id) > 10:
            bot.send_video(chat_id, file_path_or_id)
    except Exception as e:
        print(f"Video skipped safely: {e}")

# /start Command Handler
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # STEP 1: BUTTONS & WELCOME TEXT FIRST (Instant Response Guaranteed!)
    welcome_text = (
        f"🔥 **Welcome to Premium Bot!**\n\n"
        f"Hello [{user_name}](tg://user?id={user_id})!\n\n"
        f"Niche diye gaye buttons mein se apna plan chunhein:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

    # STEP 2: TRY SENDING INTRO VIDEO IN BACKGROUND (If available)
    try_send_video(message.chat.id, "video1.mp4")

# /broadcast Command Handler (Admin Only)
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "📢 Broadcast ke liye message bhejien:")
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

# Buttons Callback Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data.startswith("b"):
        # Plan message with Back Button
        msg_text = f"✅ Aapne **{data.upper()}** select kiya hai.\n\nIs plan ki details niche hain:"
        bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=get_back_keyboard())
        
        # Try sending sample video for button (if exists in root)
        try_send_video(chat_id, "video2.mp4")

    elif data == "help":
        help_text = "*Help & Support*\n\nKisi bhi sahayata ke liye Admin se sampark karein."
        bot.send_message(chat_id, help_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "back":
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options mein se chunhein:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.polling(non_stop=True, skip_pending=True)
