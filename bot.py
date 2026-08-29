import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Render Web Service / UptimeRobot ke liye Flask Server
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive and running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# Bot Token aur Admin ID Settings
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8618601267:AAFs9jI9kIVK13vQGgrv5egFm-XjNSQBqFc")
ADMIN_ID = os.environ.get("ADMIN_ID", "123456789")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Step 1: Pehle User ko Task Message milega
    task_text = (
        "📋 **Task:**\n"
        "Humare official updates ke liye channel ko join karein aur sabhi niyam padhein."
    )
    await update.message.reply_text(task_text, parse_mode="Markdown")

    # Step 2: Main Keyboard Layout (10 Verticals + Last Row Mein 2 Side-by-Side)
    keyboard = [
        [InlineKeyboardButton("⭐ Premium Option 1", callback_data="opt_1")],
        [InlineKeyboardButton("⭐ Premium Option 2", callback_data="opt_2")],
        [InlineKeyboardButton("⭐ Premium Option 3", callback_data="opt_3")],
        [InlineKeyboardButton("⭐ Premium Option 4", callback_data="opt_4")],
        [InlineKeyboardButton("⭐ Premium Option 5", callback_data="opt_5")],
        [InlineKeyboardButton("⭐ Premium Option 6", callback_data="opt_6")],
        [InlineKeyboardButton("⭐ Premium Option 7", callback_data="opt_7")],
        [InlineKeyboardButton("⭐ Premium Option 8", callback_data="opt_8")],
        [InlineKeyboardButton("⭐ Premium Option 9", callback_data="opt_9")],
        [InlineKeyboardButton("⭐ Premium Option 10", callback_data="opt_10")],
        
        # Aakhri row: Left mein Help aur Right mein Admin button
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("📩 Admin", url=f"tg://user?id={ADMIN_ID}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Step 3: Hello [User Name] ke saath Welcome Message
    welcome_msg = (
        f"Hello {user.mention_markdown_v2()}\!\n\n"
        "Aapka hamare Telegram Premium Bot mein swagat hai\.\n"
        "Kripya niche diye gaye options mein se chunhein:"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="MarkdownV2")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("opt_"):
        num = data.split("_")[1]
        msg = f"Aapne **Option {num}** select kiya hai!"
        back_keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]]
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

    elif data == "help":
        msg = "ℹ️ **Help & Support**\n\nKisi bhi dikkat ke liye Admin se sampark karein."
        back_keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]]
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

    elif data == "back_to_menu":
        user = query.from_user
        keyboard = [
            [InlineKeyboardButton("⭐ Premium Option 1", callback_data="opt_1")],
            [InlineKeyboardButton("⭐ Premium Option 2", callback_data="opt_2")],
            [InlineKeyboardButton("⭐ Premium Option 3", callback_data="opt_3")],
            [InlineKeyboardButton("⭐ Premium Option 4", callback_data="opt_4")],
            [InlineKeyboardButton("⭐ Premium Option 5", callback_data="opt_5")],
            [InlineKeyboardButton("⭐ Premium Option 6", callback_data="opt_6")],
            [InlineKeyboardButton("⭐ Premium Option 7", callback_data="opt_7")],
            [InlineKeyboardButton("⭐ Premium Option 8", callback_data="opt_8")],
            [InlineKeyboardButton("⭐ Premium Option 9", callback_data="opt_9")],
            [InlineKeyboardButton("⭐ Premium Option 10", callback_data="opt_10")],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("📩 Admin", url=f"tg://user?id={ADMIN_ID}")
            ]
        ]
        welcome_msg = (
            f"Hello {user.mention_markdown_v2()}\!\n\n"
            "Kripya niche diye gaye options mein se chunhein:"
        )
        await query.edit_message_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="MarkdownV2")

def main():
    # Flask Server Start Karein (Render Web Service ke liye)
    keep_alive()

    if not BOT_TOKEN:
        print("Error: BOT_TOKEN sahi se set nahi hai!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is successfully running...")
    app.run_polling()

if __name__ == '__main__':
    main()
