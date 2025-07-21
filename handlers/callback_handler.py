def register_callback_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("quality|"))
    def handle_quality_selection(call):
        try:
            _, quality, link = call.data.split("|", 2)
        except ValueError:
            bot.answer_callback_query(call.id, "Invalid callback data.")
            return

        bot.answer_callback_query(call.id, f"Quality {quality} kbps selected.")
        bot.send_message(call.message.chat.id, f"You selected {quality} kbps for link:\n{link}")
