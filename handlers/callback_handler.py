"""
Callback handler for Spotify Bot.

This module handles inline keyboard callbacks with improved error handling,
progress updates, and multilingual support.
"""

import threading
from threading import Semaphore

from telebot import TeleBot
from telebot.types import CallbackQuery

from config import config
from utils.logging_config import setup_logging, log_user_action
from utils.i18n import get_messages
from utils.downloader import download_and_send
from utils.spotify_utils import validate_spotify_url
from .spotify_handler import (
    consume_stored_link_data,
    format_metadata_html,
    get_stored_link_data,
)

logger = setup_logging(__name__)

# Limit concurrent downloads to prevent DoS
_download_semaphore = Semaphore(config.max_concurrent_downloads)


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

        # Peek first so a request is not consumed while all worker slots are
        # occupied. The user can tap the same button again after a short wait.
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

        # Do not create unbounded threads that merely wait on a semaphore.
        # Keeping the stored link intact on saturation makes overload bounded
        # and lets the same callback be retried later.
        if not _download_semaphore.acquire(blocking=False):
            try:
                bot.answer_callback_query(call.id, messages.get("server_busy"))
            except Exception as e:
                logger.warning("Failed to report busy download queue: %s", e)
            return

        # Atomically consume only after a worker slot is reserved. This still
        # prevents double taps/replayed payloads from starting duplicates.
        link_data = consume_stored_link_data(link_id, user_id)
        if not link_data:
            _download_semaphore.release()
            try:
                bot.answer_callback_query(call.id, messages.get("link_not_found"))
            except Exception as e:
                logger.warning("Failed to report consumed callback: %s", e)
            return

        spotify_url = link_data["link"]
        metadata = link_data.get("metadata", {})

        # Log quality selection
        log_user_action(
            logger,
            user_id,
            "Quality selected",
            f"Quality: {quality}kbps, URL: {spotify_url[:50]}...",
        )

        # A callback acknowledgement is best-effort UI. The link has already
        # been consumed, so a transient Telegram error here must never prevent
        # the actual download from starting.
        try:
            bot.answer_callback_query(
                call.id, messages.get("quality_selected", quality=quality)
            )
        except Exception as e:
            logger.warning("Failed to acknowledge quality callback: %s", e)

        # Update message to show download progress
        try:
            progress_text = messages.get("downloading", quality=quality)

            # Spotify metadata is untrusted text. Render it as escaped HTML so
            # titles containing Markdown metacharacters cannot break the reply.
            metadata_text = format_metadata_html(metadata)
            if metadata_text:
                progress_text = (
                    f"{metadata_text}\n\n"
                    f"⏳ {messages.get('downloading', quality=quality)}"
                )

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=progress_text,
                reply_markup=None,  # Remove the inline keyboard
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Failed to update progress message: %s", e)
            # Continue with the download even if all status-message updates
            # fail. A cosmetic Telegram request must not block delivery.
            try:
                status_kwargs = {}
                thread_id = getattr(call.message, "message_thread_id", None)
                if thread_id is not None:
                    status_kwargs["message_thread_id"] = thread_id
                bot.send_message(
                    chat_id,
                    messages.get("downloading", quality=quality),
                    **status_kwargs,
                )
            except Exception as status_error:
                logger.warning("Failed to send fallback progress message: %s", status_error)

        def _download_worker():
            try:
                download_and_send(
                    bot,
                    call.message,
                    spotify_url,
                    quality,
                    user_id=user_id,
                )
            except Exception as e:
                logger.error("Download failed for user %s: %s", user_id, e)

                # download_and_send already contains its own error boundary; this
                # is only a final guard for truly unexpected worker failures.
                try:
                    bot.send_message(chat_id, messages.get("unexpected_error"))
                except Exception:
                    logger.exception("Failed to report worker error to chat %s", chat_id)
            finally:
                _download_semaphore.release()

        try:
            threading.Thread(target=_download_worker, daemon=True).start()
        except Exception:
            _download_semaphore.release()
            logger.exception("Failed to start download worker for user %s", user_id)
            try:
                bot.send_message(chat_id, messages.get("unexpected_error"))
            except Exception:
                logger.exception(
                    "Failed to report worker start failure to chat %s", chat_id
                )

    @bot.callback_query_handler(func=lambda call: True)
    def handle_unknown_callback(call: CallbackQuery):
        """Handle unknown or invalid callbacks."""
        user_id = call.from_user.id

        logger.warning("Unknown callback from user %s: %s", user_id, call.data)

        messages = get_messages(user_id)
        bot.answer_callback_query(call.id, messages.get("invalid_callback"))
