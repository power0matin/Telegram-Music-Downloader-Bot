from utils.downloader import download_and_send
from telebot.types import CallbackQuery


def register_callback_handler(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call: CallbackQuery):
        if not call.data:
            bot.send_message(call.message.chat.id, "No data received in the callback.")
            return

        try:
            quality, spotify_link = call.data.split("|")
            download_and_send(bot, call.message, spotify_link, quality)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Error: {str(e)}")
