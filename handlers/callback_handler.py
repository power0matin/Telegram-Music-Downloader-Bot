from telebot.types import CallbackQuery
from utils.downloader import download_and_send
from spotify_handler import retrieve_link, is_spotify_url


def register_callback_handler(bot):
    @bot.callback_query_handler(
        func=lambda call: call.data and call.data.startswith("quality|")
    )
    def handle_quality_selection(call: CallbackQuery):
        try:
            _, quality_str, link_id = call.data.split("|", 2)
            quality = int(quality_str)
            if quality not in [128, 320]:
                raise ValueError("Invalid quality selected")
        except (ValueError, IndexError):
            bot.answer_callback_query(call.id, "❌ داده callback نامعتبر است.")
            return

        link = retrieve_link(link_id)
        if not link:
            bot.answer_callback_query(call.id, "❌ لینک یافت نشد یا منقضی شده است.")
            return

        if not is_spotify_url(link):
            bot.answer_callback_query(call.id, "❌ لینک معتبر Spotify نیست.")
            return

        bot.answer_callback_query(
            call.id,
            f"🎵 کیفیت {quality} کیلوبیت بر ثانیه انتخاب شد. دانلود شروع می‌شود...",
        )

        # Edit the original message to prevent duplicate prompts
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎵 در حال دانلود با کیفیت {quality} kbps...\nلطفاً صبر کنید.",
            reply_markup=None,  # Remove the inline keyboard
        )

        try:
            download_and_send(bot, call.message, link, quality)
        except Exception as e:
            bot.send_message(
                call.message.chat.id,
                f"❌ دانلود با خطا مواجه شد: {str(e)}",
            )
            bot.answer_callback_query(call.id, "خطا در دانلود.")
