"""
Spotify URL handler for Spotify Bot.

This module handles Spotify URL processing with rate limiting,
validation, and improved user experience.
"""

from __future__ import annotations

import hashlib
import html
import math
import re
import time
from threading import RLock
from typing import Dict, Optional

from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from utils.i18n import get_messages
from utils.logging_config import setup_logging, log_user_action
from utils.queue_functions import add_to_queue
from utils.rate_limiter import check_rate_limit
from utils.spotify_utils import (
    validate_spotify_url,
    sanitize_spotify_url,
    get_spotify_metadata,
    get_canonical_spotify_url,
)

logger = setup_logging(__name__)


class LinkStore:
    """
    In-memory link storage with expiration and basic cleanup.

    Stores:
        - canonical Spotify URL
        - user id
        - optional metadata snapshot
    """

    def __init__(self, expiry_seconds: int = 3600) -> None:
        """
        Initialize link store.

        Args:
            expiry_seconds: Link expiry time in seconds (default: 1 hour)
        """
        self.store: Dict[str, Dict] = {}
        self.expiry_seconds = expiry_seconds
        self._lock = RLock()

    def generate_link_id(self, link: str, user_id: int) -> str:
        """
        Generate a unique ID for the link.

        Args:
            link: Spotify URL
            user_id: User ID for additional uniqueness

        Returns:
            Unique link ID
        """
        data = f"{link}:{user_id}:{time.time_ns()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:12]

    def store_link(
        self, link_id: str, link: str, user_id: int, metadata: Optional[Dict] = None
    ) -> None:
        """
        Store link with metadata and expiry.

        Args:
            link_id: Unique link identifier
            link: Canonical Spotify URL
            user_id: User ID
            metadata: Optional metadata snapshot
        """
        with self._lock:
            self.store[link_id] = {
                "link": link,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": time.time(),
            }
            self._cleanup_expired_locked()

    def retrieve_link(
        self, link_id: str, user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Retrieve link information.

        Args:
            link_id: Link identifier
            user_id: Optional user ID for validation

        Returns:
            Link information or None if not found/expired
        """
        with self._lock:
            self._cleanup_expired_locked()

            link_data = self.store.get(link_id)
            if not link_data:
                return None

            if user_id is not None and link_data["user_id"] != user_id:
                return None

            return dict(link_data)

    def consume_link(self, link_id: str, user_id: int) -> Optional[Dict]:
        """Atomically retrieve and remove a link so one callback starts one download."""
        with self._lock:
            self._cleanup_expired_locked()
            link_data = self.store.get(link_id)
            if not link_data or link_data["user_id"] != user_id:
                return None

            self.store.pop(link_id, None)
            return dict(link_data)

    def _cleanup_expired(self) -> None:
        """Remove expired links."""
        with self._lock:
            self._cleanup_expired_locked()

    def _cleanup_expired_locked(self) -> None:
        """Remove expired links while the store lock is held."""
        current_time = time.time()
        expired_keys = [
            key
            for key, data in self.store.items()
            if current_time - data["created_at"] > self.expiry_seconds
        ]

        for key in expired_keys:
            self.store.pop(key, None)

        if expired_keys:
            logger.debug("Cleaned up %d expired links", len(expired_keys))


# Global link store instance
link_store = LinkStore()


def register_spotify_handler(bot: TeleBot) -> None:
    """
    Register Spotify URL message handler.

    Args:
        bot: Telegram bot instance
    """

    @bot.message_handler(func=lambda message: _is_spotify_message(message))
    def handle_spotify_url(message: Message) -> None:
        """Handle Spotify URL messages."""
        user_id = message.from_user.id
        chat_id = message.chat.id

        messages = get_messages(user_id)

        # Rate limiting
        is_allowed, time_until_allowed = check_rate_limit(user_id)
        if not is_allowed:
            log_user_action(
                logger,
                user_id,
                "Rate limited",
                f"Wait: {time_until_allowed:.1f}s",
            )
            wait_seconds = max(1, math.ceil(time_until_allowed or 1))
            bot.reply_to(
                message,
                messages.get("rate_limit_exceeded", seconds=wait_seconds),
            )
            return

        raw_text = (message.text or "").strip()
        if not raw_text:
            bot.reply_to(message, messages.get("invalid_url"))
            return

        # Sanitize URL (strip query params, normalize)
        sanitized_url = sanitize_spotify_url(raw_text)

        # Validate URL
        if not validate_spotify_url(sanitized_url):
            log_user_action(logger, user_id, "Invalid URL", sanitized_url[:50])
            bot.reply_to(message, messages.get("invalid_url"))
            return

        # Canonical URL for storage / logging / download
        canonical_url = get_canonical_spotify_url(sanitized_url) or sanitized_url

        log_user_action(logger, user_id, "Valid Spotify URL", canonical_url[:50])

        # Fetch metadata (best effort, non-critical)
        try:
            metadata = get_spotify_metadata(canonical_url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to get metadata for %s: %s", canonical_url, exc)
            metadata = {"valid": False, "error": str(exc)}

        # Store link
        link_id = link_store.generate_link_id(canonical_url, user_id)
        link_store.store_link(link_id, canonical_url, user_id, metadata)

        # Add to queue for tracking
        add_to_queue(canonical_url, chat_id)

        # Inline keyboard for quality selection
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(
                messages.get("quality_128"),
                callback_data=f"quality|128|{link_id}",
            ),
            InlineKeyboardButton(
                messages.get("quality_320"),
                callback_data=f"quality|320|{link_id}",
            ),
        )

        # Prepare response text with metadata
        response_text = messages.get("link_detected")
        metadata_text = format_metadata_html(metadata)
        if metadata_text:
            response_text += f"\n\n{metadata_text}"

        bot.reply_to(
            message,
            response_text,
            reply_markup=markup,
            parse_mode="HTML",
        )

    @bot.message_handler(
        func=lambda message: bool(getattr(message, "text", None))
        and not _is_spotify_message(message)
        and not message.text.startswith("/")
    )
    def handle_non_spotify_message(message: Message) -> None:
        """Handle non-Spotify messages."""
        user_id = message.from_user.id
        messages = get_messages(user_id)

        if not message.text:
            bot.reply_to(message, messages.get("text_only"))
            return

        text = message.text.strip()
        if text.startswith("http"):
            log_user_action(logger, user_id, "Non-Spotify URL", text[:50])
            bot.reply_to(message, messages.get("invalid_url"))
        else:
            bot.reply_to(message, messages.get("welcome"))


def _is_spotify_message(message: Message) -> bool:
    """
    Quick check if message text looks like a Spotify URL/URI.

    Note: This is a cheap filter; full validation is done later.
    """
    text = getattr(message, "text", None)
    if not text:
        return False

    lowered = text.strip().lower()
    return (
        "open.spotify.com" in lowered
        or re.search(r'(?<![a-z0-9-])spotify\.com(?:/|$)', lowered) is not None
        or lowered.startswith("spotify:")
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


def consume_stored_link_data(link_id: str, user_id: int) -> Optional[Dict]:
    """Atomically consume stored callback data for a single download attempt."""
    return link_store.consume_link(link_id, user_id)


def format_metadata_html(metadata: Dict) -> str:
    """Build Telegram-safe HTML metadata text from untrusted track metadata."""
    if not metadata.get("valid") or not metadata.get("title"):
        return ""

    title = html.escape(str(metadata.get("title") or "Unknown"))
    artist = metadata.get("artist")
    text = f"🎵 <b>{title}</b>"
    if artist:
        text += f"\n👤 {html.escape(str(artist))}"
    return text
