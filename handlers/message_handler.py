from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue_functions import add_to_queue

def register_message_handler(bot):
    @bot.message_handler(func=lambda message: True)
    def handle_spotify_link(message: Message):
        if not message.text or not message.text.startswith("http"):
            bot.reply_to(message, "Invalid link.")
            return

        link = message.text.strip()
        add_to_queue(link, message.chat.id)

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("128 kbps", callback_data=f"quality|128|{link}"),
            InlineKeyboardButton("320 kbps", callback_data=f"quality|320|{link}")
        )
        bot.reply_to(message, "Please select your desired quality:", reply_markup=markup)
