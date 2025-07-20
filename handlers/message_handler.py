from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


def register_message_handler(bot):
    @bot.message_handler(func=lambda message: True)
    def handle_spotify_link(message: Message):
        if not message.text:
            bot.reply_to(message, "Invalid link.")
            return
        spotify_link = message.text.strip()
        if not spotify_link.startswith("http"):
            bot.reply_to(message, "Invalid link.")
            return

        data_128 = f"128|{spotify_link}"[:64]
        data_320 = f"320|{spotify_link}"[:64]

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("128 kbps", callback_data=data_128),
            InlineKeyboardButton("320 kbps", callback_data=data_320),
        )

        bot.reply_to(
            message, "Please select your desired quality:", reply_markup=markup
        )
