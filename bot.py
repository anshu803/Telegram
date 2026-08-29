import os
import logging
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, BotCommand

logging.basicConfig(level=logging.INFO)

# Flask Server (Render Uptime Support)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running online!"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.daemon = True
    t.start()

# Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

bot = telebot.TeleBot(BOT_TOKEN)

# User list storage for broadcast
users_list = set()

# Side Menu Bar Commands Setup
try:
    bot.set_my_commands([
        BotCommand("start", "Start Bot Menu"),
        BotCommand("broadcast", "Send Broadcast (Admin Only)")
    ])
except Exception as e:
    print(f"Command set error: {e}")

# Main Keyboard Structure
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    
    # 10 Vertical Buttons (Custom Names & Pricing)
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

# Back Button
def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="back"))
    return markup

# Helper: 3 Videos Ek Sath (Album Format) Send karne ke liye
def send_3_videos_group(chat_id, v1_path, v2_path, v3_path, caption_text):
    paths = [v1_path, v2_path, v3_path]
    files_to_close = []
    media_group = []

    for index, path in enumerate(paths):
        if os.path.exists(path):
            f = open(path, 'rb')
            files_to_close.append(f)
            cap = caption_text if index == 0 else ""
            media_group.append(InputMediaVideo(f, caption=cap, parse_mode="Markdown"))

    if media_group:
        bot.send_media_group(chat_id, media_group)
        for f in files_to_close:
            f.close()
        bot.send_message(chat_id, "Wapas jane ke liye button dabayein:", reply_markup=get_back_keyboard())
    else:
        bot.send_message(
            chat_id, 
            f"{caption_text}\n\n*(Note: Videos missing hain folder me)*", 
            parse_mode="Markdown", 
            reply_markup=get_back_keyboard()
        )

# /start Command Handler
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users_list.add(message.chat.id)
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    intro_caption = (
        f"**Welcome to Premium Bot!**\n\n"
        f"Hello [{user_name}](tg://user?id={user_id})!\n"
        "Ye aapke liye intro videos hain."
    )

    # 1. Pehle 3 Videos ek sath aayengi
    send_3_videos_group(
        message.chat.id, 
        "videos/start1.mp4", 
        "videos/start2.mp4", 
        "videos/start3.mp4", 
        intro_caption
    )

    # 2. Phir Text Message aur Saare Buttons
    welcome_msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options me se chunhein:"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# /broadcast Command Handler (Admin Side-Menu Feature)
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Aap Admin nahi hain!")
        return

    msg = bot.reply_to(message, "Broadcast ke liye text, photo ya video message bhein:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    count = 0
    for user_id in users_list:
        try:
            bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
        except Exception:
            pass
    bot.send_message(message.chat.id, f"Broadcast successfully {count} users ko bhej diya gaya!")

# Button Click Handling
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # Har Button Click par 3 Videos Ek Sath (Media Group)
    if data == "b1":
        cap = "*VIP Movie Plan (Pricing: ₹199)*\n\nVIP Movie Content Preview."
        send_3_videos_group(chat_id, "videos/b1_1.mp4", "videos/b1_2.mp4", "videos/b1_3.mp4", cap)

    elif data == "b2":
        cap = "*Trading Signals (Pricing: ₹499)*\n\nVIP Trading Signals Demo."
        send_3_videos_group(chat_id, "videos/b2_1.mp4", "videos/b2_2.mp4", "videos/b2_3.mp4", cap)

    elif data == "b3":
        cap = "*Premium Course (Pricing: ₹299)*\n\nCourse Details Video."
        send_3_videos_group(chat_id, "videos/b3_1.mp4", "videos/b3_2.mp4", "videos/b3_3.mp4", cap)

    elif data == "b4":
        cap = "*Pro Software Pack (Pricing: ₹399)*\n\nSoftware Previews."
        send_3_videos_group(chat_id, "videos/b4_1.mp4", "videos/b4_2.mp4", "videos/b4_3.mp4", cap)

    elif data == "b5":
        cap = "*Private Channel Access (Pricing: ₹999)*\n\nChannel Membership Info."
        send_3_videos_group(chat_id, "videos/b5_1.mp4", "videos/b5_2.mp4", "videos/b5_3.mp4", cap)

    elif data == "b6":
        cap = "*Special Combo Offer (Pricing: ₹599)*\n\nCombo Offer Demos."
        send_3_videos_group(chat_id, "videos/b6_1.mp4", "videos/b6_2.mp4", "videos/b6_3.mp4", cap)

    elif data == "b7":
        cap = "*AI Tools Access (Pricing: ₹349)*\n\nAI Pack Videos."
        send_3_videos_group(chat_id, "videos/b7_1.mp4", "videos/b7_2.mp4", "videos/b7_3.mp4", cap)

    elif data == "b8":
        cap = "*Referral Program (Pricing: FREE)*\n\nRefer & Earn Videos."
        send_3_videos_group(chat_id, "videos/b8_1.mp4", "videos/b8_2.mp4", "videos/b8_3.mp4", cap)

    elif data == "b9":
        cap = "*Lifetime Membership (Pricing: ₹1499)*\n\nLifetime VIP Access."
        send_3_videos_group(chat_id, "videos/b9_1.mp4", "videos/b9_2.mp4", "videos/b9_3.mp4", cap)

    elif data == "b10":
        cap = "*Exclusive VIP Pack (Pricing: ₹1999)*\n\nExclusive Content."
        send_3_videos_group(chat_id, "videos/b10_1.mp4", "videos/b10_2.mp4", "videos/b10_3.mp4", cap)

    elif data == "help":
        help_text = "*Help & Support*\n\nAdmin se sampark karein."
        bot.send_message(chat_id, help_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "back":
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options me se chunhein:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    # Safe polling mode fix for Python 3.14/Render
    bot.polling(non_stop=True, skip_pending=True)
