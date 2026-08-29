import os
import logging
from threading import Thread
from flask import Flask, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, BotCommand

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------
# RENDER WEB SERVICE & UPTIMEROBOT SUPPORT
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Web Service is running perfectly!"

# UptimeRobot / Ping Endpoint (Is URL ko UptimeRobot par add karein)
@app.route('/ping')
def ping():
    return jsonify(status="alive", code=200)

def run_flask():
    # Render environment variable se PORT fetch karta hai (default 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ---------------------------------------------------------
# TELEGRAM BOT SETUP
# ---------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN)
users_list = set()

# Menu Bar Commands Setup (/start & /broadcast)
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
    
    # Bottom Row: Help (Left) & Admin (Right) Side-by-Side
    btn_help = InlineKeyboardButton("Help", callback_data="help")
    btn_admin = InlineKeyboardButton("Admin", url=f"tg://user?id={ADMIN_ID}")
    markup.row(btn_help, btn_admin)
    return markup

def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="back"))
    return markup

# 3 Videos Media Group Helper
def send_3_videos(chat_id, v1_path, v2_path, v3_path, caption_text):
    paths = [v1_path, v2_path, v3_path]
    files_to_close = []
    media_group = []

    for index, path in enumerate(paths):
        if os.path.exists(path):
            f = open(path, 'rb')
            files_to_close.append(f)
            cap = caption_text if index == 0 else ""
            media_group.append(InputMediaVideo(f, caption=cap, parse_mode="Markdown"))
        elif isinstance(path, str) and not path.endswith('.mp4'):
            cap = caption_text if index == 0 else ""
            media_group.append(InputMediaVideo(path, caption=cap, parse_mode="Markdown"))

    if media_group:
        try:
            bot.send_media_group(chat_id, media_group)
        except Exception as e:
            print(f"Error sending videos: {e}")
            bot.send_message(chat_id, caption_text, parse_mode="Markdown")
        finally:
            for f in files_to_close:
                f.close()
    else:
        bot.send_message(chat_id, caption_text, parse_mode="Markdown")

# /start Command Handler
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    intro_caption = f"🔥 **Welcome to Premium Bot!**\n\nHello [{user_name}](tg://user?id={user_id})!\nYe aapke liye Intro Videos hain."
    
    # 1. Pehle 3 Videos Aayengi
    send_3_videos(
        message.chat.id, 
        "videos/start1.mp4", 
        "videos/start2.mp4", 
        "videos/start3.mp4", 
        intro_caption
    )

    # 2. Phir Welcome Message aur Subhi Buttons Aayenge
    welcome_text = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options mein se chunhein:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# /broadcast Command Handler (Admin Only)
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "📢 Broadcast ke liye text, photo ya video bhejien:")
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

# Callback Buttons Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "b1":
        cap = "*VIP Movie Plan (Pricing: ₹199)*\n\nVIP Movie Content Preview."
        send_3_videos(chat_id, "videos/b1_1.mp4", "videos/b1_2.mp4", "videos/b1_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b2":
        cap = "*Trading Signals (Pricing: ₹499)*\n\nTrading VIP Signals Demo."
        send_3_videos(chat_id, "videos/b2_1.mp4", "videos/b2_2.mp4", "videos/b2_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b3":
        cap = "*Premium Course (Pricing: ₹299)*\n\nCourse Details Video."
        send_3_videos(chat_id, "videos/b3_1.mp4", "videos/b3_2.mp4", "videos/b3_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b4":
        cap = "*Pro Software Pack (Pricing: ₹399)*\n\nSoftware Previews."
        send_3_videos(chat_id, "videos/b4_1.mp4", "videos/b4_2.mp4", "videos/b4_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b5":
        cap = "*Private Channel Access (Pricing: ₹999)*\n\nChannel Membership Info."
        send_3_videos(chat_id, "videos/b5_1.mp4", "videos/b5_2.mp4", "videos/b5_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b6":
        cap = "*Special Combo Offer (Pricing: ₹599)*\n\nCombo Offer Demos."
        send_3_videos(chat_id, "videos/b6_1.mp4", "videos/b6_2.mp4", "videos/b6_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b7":
        cap = "*AI Tools Access (Pricing: ₹349)*\n\nAI Pack Videos."
        send_3_videos(chat_id, "videos/b7_1.mp4", "videos/b7_2.mp4", "videos/b7_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b8":
        cap = "*Referral Program (Pricing: FREE)*\n\nRefer & Earn Videos."
        send_3_videos(chat_id, "videos/b8_1.mp4", "videos/b8_2.mp4", "videos/b8_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b9":
        cap = "*Lifetime Membership (Pricing: ₹1499)*\n\nLifetime VIP Access."
        send_3_videos(chat_id, "videos/b9_1.mp4", "videos/b9_2.mp4", "videos/b9_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "b10":
        cap = "*Exclusive VIP Pack (Pricing: ₹1999)*\n\nExclusive Content."
        send_3_videos(chat_id, "videos/b10_1.mp4", "videos/b10_2.mp4", "videos/b10_3.mp4", cap)
        bot.send_message(chat_id, "Wapas jane ke liye click karein:", reply_markup=get_back_keyboard())

    elif data == "help":
        help_text = "*Help & Support*\n\nAdmin se sampark karein."
        bot.send_message(chat_id, help_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "back":
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options mein se chunhein:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.polling(non_stop=True, skip_pending=True)
