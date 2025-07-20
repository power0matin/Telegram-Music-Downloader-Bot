from telebot.types import Message


def register_start_handler(bot):
    @bot.message_handler(commands=["start"])
    def send_welcome(message: Message):
        bot.reply_to(
            message,
            "Hello! Please send the Spotify link for the song, album, or playlist you want to download.",
        )
