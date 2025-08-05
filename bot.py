import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telebot import TeleBot
from handlers.spotify_handler import register_message_handler
from config import BOT_TOKEN

if not BOT_TOKEN:
    print(
        "Error: BOT_TOKEN is required. Please set the BOT_TOKEN environment variable."
    )
    print("Example: export BOT_TOKEN='your_bot_token_here'")
    sys.exit(1)

try:
    bot = TeleBot(BOT_TOKEN)
    register_message_handler(bot)

    print("Bot is running...")
    bot.infinity_polling()
except Exception as e:
    print(f"Error starting bot: {e}")
    sys.exit(1)
