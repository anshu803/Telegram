import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Flask Server (Render Service Alive Rakhne Ke Liye)
app = Flask('')

@app.route('/')
def home():
    return "Bot Alive"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.daemon = True
    t.start()

# Bot Token & Admin ID Setup
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = os.environ.get("ADMIN_ID", "123456789")

bot = telebot.TeleBot(BOT_TOKEN)

# Main Keyboard Structure (Pricing & Unique Names Ke Sath)
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    
    # 10 Vertical Buttons (Har button ka alag naam aur pricing)
    markup.add(InlineKeyboardButton("🎬 VIP Movie Plan - ₹199", callback_data="b1"))
    markup.add(InlineKeyboardButton("📊 Trading Signals - ₹499", callback_data="b2"))
    markup.add(InlineKeyboardButton("📘 Premium Course - ₹299", callback_data="b3"))
    markup.add(InlineKeyboardButton("🛠️ Pro Software Pack - ₹399", callback_data="b4"))
    markup.add(InlineKeyboardButton("👑 Private Channel Access - ₹999", callback_data="b5"))
    markup.add(InlineKeyboardButton("🎁 Special Combo Offer - ₹599", callback_data="b6"))
    markup.add(InlineKeyboardButton("🚀 AI Tools Access - ₹349", callback_data="b7"))
    markup.add(InlineKeyboardButton("👥 Referral Program - Free", callback_data="b8"))
    markup.add(InlineKeyboardButton("🔥 Lifetime Membership - ₹1499", callback_data="b9"))
    markup.add(InlineKeyboardButton("💎 Exclusive VIP Pack - ₹1999", callback_data="b10"))
    
    # Last Row: Left (Help) & Right (Admin) Side-by-Side
    btn_help = InlineKeyboardButton("ℹ️ Help", callback_data="help")
    btn_admin = InlineKeyboardButton("📩 Admin", url=f"tg://user?id={ADMIN_ID}")
    markup.row(btn_help, btn_admin)
    
    return markup

# Back Button
def get_back_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back"))
    return markup

# /start Command Handler (Seedhe Welcome Message Aayega)
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    
    welcome_msg = (
        f"Hello [{user_name}](tg://user?id={user_id})!\n\n"
        "Aapka hamare Premium Bot mein swagat hai.\n"
        "Kripya niche diye gaye plans mein se apna option chunhein:"
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# Video Send Karne Ka Helper Function (Video + Caption Text)
def send_button_video(chat_id, video_path, text_caption):
    if os.path.exists(video_path):
        with open(video_path, 'rb') as v:
            bot.send_video(chat_id, v, caption=text_caption, parse_mode="Markdown", reply_markup=get_back_keyboard())
    else:
        # Agar video folder mein nahi milli toh text message bhejega
        error_text = f"{text_caption}\n\n*(Note: Video file `{video_path}` missing hai, kripya videos folder mein dalein)*"
        bot.send_message(chat_id, error_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

# Button Click Callback Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # Button 1 Response
    if data == "b1":
        caption = "🎬 *VIP Movie Plan (Pricing: ₹199)*\n\nIs plan mein aapko latest HD movies aur series ka instant download link milega."
        send_button_video(chat_id, "videos/video1.mp4", caption)

    # Button 2 Response
    elif data == "b2":
        caption = "📊 *Trading Signals Plan (Pricing: ₹499)*\n\nDaily 95%+ accurate Crypto aur Forex trading signals paane ke liye ye plan lein."
        send_button_video(chat_id, "videos/video2.mp4", caption)

    # Button 3 Response
    elif data == "b3":
        caption = "📘 *Premium Course (Pricing: ₹299)*\n\nIs course mein aapko basic se advance tak full video classes milengi."
        send_button_video(chat_id, "videos/video3.mp4", caption)

    # Button 4 Response
    elif data == "b4":
        caption = "🛠️ *Pro Software Pack (Pricing: ₹399)*\n\nIsme Android aur PC ke sabhi unlocked premium tools milenge."
        send_button_video(chat_id, "videos/video4.mp4", caption)

    # Button 5 Response
    elif data == "b5":
        caption = "👑 *Private Channel Access (Pricing: ₹999)*\n\nHamare private VIP channel ki 1-Month membership."
        send_button_video(chat_id, "videos/video5.mp4", caption)

    # Button 6 Response
    elif data == "b6":
        caption = "🎁 *Special Combo Offer (Pricing: ₹599)*\n\nMovies + Software + Courses sabhi ek hi pack mein."
        send_button_video(chat_id, "videos/video6.mp4", caption)

    # Button 7 Response
    elif data == "b7":
        caption = "🚀 *AI Tools Access (Pricing: ₹349)*\n\nBest ChatGPT aur image generation AI tools ka full access."
        send_button_video(chat_id, "videos/video7.mp4", caption)

    # Button 8 Response
    elif data == "b8":
        caption = "👥 *Referral Program (Pricing: FREE)*\n\nApne dosto ko link share karein aur har joining par commission payein."
        send_button_video(chat_id, "videos/video8.mp4", caption)

    # Button 9 Response
    elif data == "b9":
        caption = "🔥 *Lifetime Membership (Pricing: ₹1499)*\n\nEk baar pay karein aur lifetime tak sabhi premium updates payein."
        send_button_video(chat_id, "videos/video9.mp4", caption)

    # Button 10 Response
    elif data == "b10":
        caption = "💎 *Exclusive VIP Pack (Pricing: ₹1999)*\n\nAll-in-one VIP Access + Personal Admin Support."
        send_button_video(chat_id, "videos/video10.mp4", caption)

    # Help Action
    elif data == "help":
        help_text = "ℹ️ *Help & Support*\n\nKisi bhi dikkat ya payment confirmation ke liye Admin se sampark karein."
        bot.send_message(chat_id, help_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    # Back to Main Menu Action
    elif data == "back":
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        msg = f"Hello [{user_name}](tg://user?id={user_id})!\n\nKripya niche diye gaye plans mein se chunhein:"
        bot.send_message(chat_id, msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(skip_pending=True)
