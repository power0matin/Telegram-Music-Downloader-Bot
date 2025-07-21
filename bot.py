from telebot import TeleBot
from handlers.spotify_handler import register_message_handler
import os

TOKEN = os.getenv("BOT_TOKEN", "your_token_here")
bot = TeleBot(TOKEN)

register_message_handler(bot)

print("Bot is running...")
bot.infinity_polling()
