import subprocess
import sys
from telebot import TeleBot
from config import BOT_TOKEN

def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg():
    print("FFmpeg is not installed. Installing now...")
    subprocess.run(["sudo", "apt", "update"], check=True)
    subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)

if not is_ffmpeg_installed():
    install_ffmpeg()

bot = TeleBot(BOT_TOKEN)

# Register all handlers
from handlers.start_handler import register_start_handler
from handlers.message_handler import register_message_handler
from handlers.callback_handler import register_callback_handler

register_start_handler(bot)
register_message_handler(bot)
register_callback_handler(bot)

print("Bot is running...")
bot.infinity_polling()
