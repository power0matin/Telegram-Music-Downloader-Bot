"""
Callback handler for Spotify Bot.

This module handles inline keyboard callbacks with improved error handling,
progress updates, and multilingual support.
"""

import threading
from threading import Semaphore

from telebot import TeleBot
from telebot.types import CallbackQuery

from utils.logging_config import setup_logging, log_user_action
from utils.i18n import get_messages
from utils.downloader import download_and_send
from utils.spotify_utils import validate_spotify_url
from .spotify_handler import get_stored_link_data

logger = setup_logging(__name__)

# Limit concurrent downloads to prevent DoS
_download_semaphore = Semaphore(5)


def register_callback_handlers(bot: TeleBot):
    """
    Register all callback handlers.

    Args:
        bot: Telegram bot instance
    """

    @bot.callback_query_handler(
        func=lambda call: call.data and call.data.startswith("quality|")
    )
    def handle_quality_selection(call: CallbackQuery):
        """Handle quality selection callback."""
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # Get user's language
        messages = get_messages(user_id)

        try:
            # Parse callback data
            parts = call.data.split("|", 2)
            if len(parts) != 3:
                raise ValueError("Invalid callback data format")

            _, quality_str, link_id = parts
            quality = int(quality_str)

            if quality not in [128, 320]:
                raise ValueError("Invalid quality value")

        except (ValueError, IndexError) as e:
            logger.warning("Invalid callback data from user %s: %s", user_id, call.data)
            bot.answer_callback_query(call.id, messages.get("invalid_callback"))
            return

        # Retrieve stored link data
        link_data = get_stored_link_data(link_id, user_id)
        if not link_data:
            logger.warning("Link not found for user %s, link_id: %s", user_id, link_id)
            bot.answer_callback_query(call.id, messages.get("link_not_found"))
            return

        spotify_url = link_data["link"]
        metadata = link_data.get("metadata", {})

        # Validate URL again (security check)
        if not validate_spotify_url(spotify_url):
            logger.warning("Invalid Spotify URL in callback: %s", spotify_url)
            bot.answer_callback_query(call.id, messages.get("invalid_spotify_link"))
            return

        # Log quality selection
        log_user_action(
            logger,
            user_id,
            "Quality selected",
            f"Quality: {quality}kbps, URL: {spotify_url[:50]}...",
        )

        # Answer callback query
        bot.answer_callback_query(
            call.id, messages.get("quality_selected", quality=quality)
        )

        # Update message to show download progress
        try:
            progress_text = messages.get("downloading", quality=quality)

            # Add metadata to progress message if available
            if metadata.get("valid") and metadata.get("title"):
                title = metadata.get("title", "Unknown")
                artist = metadata.get("artist", "Unknown")
                progress_text = f"🎵 **{title}**"
                if artist:
                    progress_text += f"\n👤 {artist}"
                progress_text += (
                    f"\n\n⏳ {messages.get('downloading', quality=quality)}"
                )

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=progress_text,
                reply_markup=None,  # Remove the inline keyboard
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error("Failed to update progress message: %s", e)
            # Continue with download even if message update fails
            bot.send_message(chat_id, messages.get("downloading", quality=quality))

        def _download_worker():
            with _download_semaphore:
                try:
                    download_and_send(bot, call.message, spotify_url, quality, user_id=user_id)
                except Exception as e:
                    logger.error("Download failed for user %s: %s", user_id, e)

                    # Send error message
                    error_message = messages.get("unexpected_error")
                    if "rate limit" in str(e).lower():
                        error_message = messages.get("retry_failed")
                    elif "not found" in str(e).lower():
                        error_message = messages.get("no_files_downloaded")
                    elif "timeout" in str(e).lower():
                        error_message = messages.get("download_timeout")

                    bot.send_message(chat_id, error_message)

        threading.Thread(target=_download_worker, daemon=True).start()

    @bot.callback_query_handler(func=lambda call: True)
    def handle_unknown_callback(call: CallbackQuery):
        """Handle unknown or invalid callbacks."""
        user_id = call.from_user.id

        logger.warning("Unknown callback from user %s: %s", user_id, call.data)

        messages = get_messages(user_id)
        bot.answer_callback_query(call.id, messages.get("invalid_callback"))
