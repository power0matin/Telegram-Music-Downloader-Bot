from utils.downloader import download_and_send

def register_callback_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("quality|"))
    def handle_quality_selection(call):
        try:
            _, quality, link = call.data.split("|", 2)
        except ValueError:
            bot.answer_callback_query(call.id, "Invalid callback data.")
            return

        bot.answer_callback_query(call.id, f"Quality {quality} kbps selected. Starting download...")
        bot.send_message(call.message.chat.id, f"🎵 Downloading with {quality} kbps quality...\nPlease wait.")
        
        # Start the download process
        try:
            download_and_send(bot, call.message, link, quality)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Download failed: {str(e)}")
