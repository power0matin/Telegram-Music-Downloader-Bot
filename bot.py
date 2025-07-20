from telebot import TeleBot
from config import BOT_TOKEN

from handlers.start_handler import register_start_handler
from handlers.message_handler import register_message_handler
from handlers.callback_handler import register_callback_handler

bot = TeleBot(BOT_TOKEN)

# Register all handlers
register_start_handler(bot)
register_message_handler(bot)
register_callback_handler(bot)

print("Bot is running...")
bot.infinity_polling()
