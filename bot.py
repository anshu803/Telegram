import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Flask Server (Render ke liye)
app = Flask('')

@app.route('/')
def home():
    return "Bot Alive"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.daemon = True
    t.start()

# Bot Token & Admin Setup
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = os.environ.get("ADMIN_ID", "123456789")

bot = telebot.TeleBot(BOT_TOKEN)

# Main Keyboard Structure
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    
    # 10 Vertical Buttons
    markup.add(InlineKeyboardButton("⭐ Button 1", callback_data="b1"))
    markup.add(InlineKeyboardButton("⭐ Button 2", callback_data="b2"))
    markup.add(InlineKeyboardButton("⭐ Button 3", callback_data="b3"))
    markup.add(InlineKeyboardButton("⭐ Button 4", callback_data="b4"))
    markup.add(InlineKeyboardButton("⭐ Button 5", callback_data="b5"))
    markup.add(InlineKeyboardButton("⭐ Button 6", callback_data="b6"))
    markup.add(InlineKeyboardButton("⭐ Button 7", callback_data="b7"))
    markup.add(InlineKeyboardButton("⭐ Button 8", callback_data="b8"))
    markup.add(InlineKeyboardButton("⭐ Button 9", callback_data="b9"))
    markup.add(InlineKeyboardButton("⭐ Button 10", callback_data="b10"))
    
    # Last Row: Left (Help) & Right (Admin) Side-by-Side
    btn_help = InlineKeyboardButton("ℹ️ Help", callback_data="help")
    btn_admin = InlineKeyboardButton("📩 Admin", url=f"tg://user?id={ADMIN_ID}")
    markup.row(btn_help, btn_admin)
    
    return markup

# Back Button
def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back"))
    return markup

# /start Command
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    
    # Pehle Task Message
    bot.send_message(message.chat.id, "📋 *Pehle hamara channel join karein aur task poora karein.*", parse_mode="Markdown")
    
    # Phir Hello Name Mention ke sath Welcome & Buttons
    welcome_msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nAapka swagat hai, niche diye gaye buttons par click karein:"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# Button Click Actions
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # Button 1 Response (Video Example)
    if data == "b1":
        video_path = "videos/video1.mp4"
        if os.path.exists(video_path):
            with open(video_path, 'rb') as v:
                bot.send_video(chat_id, v, caption="🎥 Button 1 Response Video", reply_markup=get_back_keyboard())
        else:
            bot.edit_message_text("🎥 **Button 1 Selected!**\n\n(Video file `videos/video1.mp4` missing hai)", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())

    # Button 2 Response (Video Example)
    elif data == "b2":
        video_path = "videos/video2.mp4"
        if os.path.exists(video_path):
            with open(video_path, 'rb') as v:
                bot.send_video(chat_id, v, caption="🎬 Button 2 Response Video", reply_markup=get_back_keyboard())
        else:
            bot.edit_message_text("🎬 **Button 2 Selected!**\n\n(Video file `videos/video2.mp4` missing hai)", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())

    # Remaining Buttons Responses
    elif data == "b3":
        bot.edit_message_text("Aapne **Button 3** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b4":
        bot.edit_message_text("Aapne **Button 4** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b5":
        bot.edit_message_text("Aapne **Button 5** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b6":
        bot.edit_message_text("Aapne **Button 6** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b7":
        bot.edit_message_text("Aapne **Button 7** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b8":
        bot.edit_message_text("Aapne **Button 8** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b9":
        bot.edit_message_text("Aapne **Button 9** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "b10":
        bot.edit_message_text("Aapne **Button 10** dabaya hai.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())
    
    # Help Action
    elif data == "help":
        bot.edit_message_text("ℹ️ **Help & Support:** Admin se baat karein.", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=get_back_keyboard())

    # Back Action
    elif data == "back":
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nNiche diye gaye options mein se chunhein:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(skip_pending=True)
