"""
Spotify URL handler for Spotify Bot.

This module handles Spotify URL processing with rate limiting,
validation, and improved user experience.
"""

import hashlib
import time
from typing import Dict, Optional

from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils.logging_config import setup_logging, log_user_action
from utils.i18n import get_messages
from utils.rate_limiter import check_rate_limit
from utils.spotify_utils import (
    validate_spotify_url,
    sanitize_spotify_url,
    get_spotify_metadata,
)
from utils.queue_functions import add_to_queue
from config import config

logger = setup_logging(__name__)


class LinkStore:
    """
    Enhanced link storage with expiration and cleanup.
    """

    def __init__(self, expiry_seconds: int = 3600):
        """
        Initialize link store.

        Args:
            expiry_seconds: Link expiry time in seconds (default: 1 hour)
        """
        self.store: Dict[str, Dict] = {}
        self.expiry_seconds = expiry_seconds

    def generate_link_id(self, link: str, user_id: int) -> str:
        """
        Generate a unique ID for the link.

        Args:
            link: Spotify URL
            user_id: User ID for additional uniqueness

        Returns:
            Unique link ID
        """
        # Include user ID and timestamp for better uniqueness
        data = f"{link}:{user_id}:{int(time.time())}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def store_link(self, link_id: str, link: str, user_id: int, metadata: Dict = None):
        """
        Store link with metadata and expiry.

        Args:
            link_id: Unique link identifier
            link: Spotify URL
            user_id: User ID
            metadata: Optional metadata
        """
        self.store[link_id] = {
            "link": link,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": time.time(),
        }

        # Clean up expired links
        self._cleanup_expired()

    def retrieve_link(self, link_id: str, user_id: int = None) -> Optional[Dict]:
        """
        Retrieve link information.

        Args:
            link_id: Link identifier
            user_id: Optional user ID for validation

        Returns:
            Link information or None if not found/expired
        """
        self._cleanup_expired()

        link_data = self.store.get(link_id)
        if not link_data:
            return None

        # Validate user if provided
        if user_id and link_data["user_id"] != user_id:
            return None

        return link_data

    def _cleanup_expired(self):
        """Remove expired links."""
        current_time = time.time()
        expired_keys = [
            key
            for key, data in self.store.items()
            if current_time - data["created_at"] > self.expiry_seconds
        ]

        for key in expired_keys:
            del self.store[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired links")


# Global link store instance
link_store = LinkStore()


def register_spotify_handler(bot: TeleBot):
    """
    Register Spotify URL message handler.

    Args:
        bot: Telegram bot instance
    """

    @bot.message_handler(func=lambda message: _is_spotify_message(message))
    def handle_spotify_url(message: Message):
        """Handle Spotify URL messages."""
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Get user's language
        messages = get_messages(user_id)

        # Check rate limit
        is_allowed, time_until_allowed = check_rate_limit(user_id)
        if not is_allowed:
            log_user_action(
                logger, user_id, "Rate limited", f"Wait: {time_until_allowed:.1f}s"
            )
            bot.reply_to(message, messages.get("rate_limit_exceeded"))
            return

        # Extract and validate URL
        text = message.text.strip()

        # Sanitize URL
        clean_url = sanitize_spotify_url(text)

        # Validate URL
        if not validate_spotify_url(clean_url):
            log_user_action(logger, user_id, "Invalid URL", clean_url[:50])
            bot.reply_to(message, messages.get("invalid_url"))
            return

        # Log valid URL processing
        log_user_action(logger, user_id, "Valid Spotify URL", clean_url[:50])

        # Get metadata (non-blocking)
        try:
            metadata = get_spotify_metadata(clean_url)
        except Exception as e:
            logger.warning(f"Failed to get metadata for {clean_url}: {e}")
            metadata = {"valid": False, "error": str(e)}

        # Generate link ID and store
        link_id = link_store.generate_link_id(clean_url, user_id)
        link_store.store_link(link_id, clean_url, user_id, metadata)

        # Add to queue for tracking
        add_to_queue(clean_url, chat_id)

        # Create quality selection keyboard
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(
                messages.get("quality_128"), callback_data=f"quality|128|{link_id}"
            ),
            InlineKeyboardButton(
                messages.get("quality_320"), callback_data=f"quality|320|{link_id}"
            ),
        )

        # Prepare response message with metadata if available
        response_text = messages.get("link_detected")
        if metadata.get("valid") and metadata.get("title"):
            title = metadata.get("title", "Unknown")
            artist = metadata.get("artist", "Unknown")
            response_text += f"\n\n🎵 **{title}**"
            if artist:
                response_text += f"\n👤 {artist}"

        bot.reply_to(message, response_text, reply_markup=markup, parse_mode="Markdown")

    @bot.message_handler(
        func=lambda message: not _is_spotify_message(message)
        and not message.text.startswith("/")
    )
    def handle_non_spotify_message(message: Message):
        """Handle non-Spotify messages."""
        user_id = message.from_user.id

        # Get user's language
        messages = get_messages(user_id)

        # Check if message contains text
        if not message.text:
            bot.reply_to(message, messages.get("text_only"))
            return

        # Check if it might be a URL but not Spotify
        text = message.text.strip()
        if text.startswith("http"):
            log_user_action(logger, user_id, "Non-Spotify URL", text[:50])
            bot.reply_to(message, messages.get("invalid_url"))
        else:
            # Send welcome message for non-URL text
            bot.reply_to(message, messages.get("welcome"))


def _is_spotify_message(message: Message) -> bool:
    """
    Check if message contains a Spotify URL.

    Args:
        message: Telegram message

    Returns:
        True if message contains Spotify URL
    """
    if not message.text:
        return False

    text = message.text.strip().lower()
    return any(
        pattern in text for pattern in ["open.spotify.com", "spotify.com", "spotify:"]
    )


def get_stored_link_data(link_id: str, user_id: int) -> Optional[Dict]:
    """
    Convenience function to get stored link data.

    Args:
        link_id: Link identifier
        user_id: User ID

    Returns:
        Link data or None
    """
    return link_store.retrieve_link(link_id, user_id)
