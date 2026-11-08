"""
Spotify URL handler for Spotify Bot.

This module handles Spotify URL processing with rate limiting,
validation, and improved user experience.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sqlite3
import time
from contextlib import closing
from pathlib import Path
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
    SQLite-backed link storage with expiry and atomic one-time consumption.

    The database lives beside the configured queue file by default, so pending
    callback data survives bot restarts while remaining local to one deployment.
    """

    def __init__(
        self,
        expiry_seconds: int = 3600,
        db_path: Optional[str | Path] = None,
    ) -> None:
        """
        Initialize the persistent link store.

        Args:
            expiry_seconds: Link expiry time in seconds (default: 1 hour).
            db_path: Optional SQLite path, primarily useful for isolated tests.
        """
        self.expiry_seconds = expiry_seconds
        default_db_path = config.queue_path.parent / "pending_links.sqlite3"
        self.db_path = str(Path(db_path or default_db_path).expanduser())
        self._lock = RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        """Open a short-lived connection with a bounded lock wait."""
        connection = sqlite3.connect(
            self.db_path, timeout=30, isolation_level=None
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    def _initialize_database(self) -> None:
        """Create the pending-link table and expiry index if needed."""
        with closing(self._connect()) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_links (
                    link_id TEXT PRIMARY KEY,
                    link TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pending_links_expires_at
                ON pending_links (expires_at)
                """
            )

        try:
            Path(self.db_path).chmod(0o600)
        except OSError:
            logger.warning("Could not restrict permissions on pending-link database")

        self.cleanup_expired()

    def generate_link_id(self, link: str, user_id: int) -> str:
        """Generate a unique ID for a pending callback."""
        data = f"{link}:{user_id}:{time.time_ns()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:12]

    def store_link(
        self, link_id: str, link: str, user_id: int, metadata: Optional[Dict] = None
    ) -> None:
        """Persist a link, owner, metadata snapshot, and absolute expiry time."""
        now = time.time()
        expires_at = now + self.expiry_seconds
        metadata_json = json.dumps(
            metadata or {}, ensure_ascii=False, separators=(",", ":")
        )

        with self._lock, closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    "DELETE FROM pending_links WHERE expires_at < ?", (now,)
                )
                connection.execute(
                    """
                    INSERT INTO pending_links (
                        link_id, link, user_id, metadata_json, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(link_id) DO UPDATE SET
                        link = excluded.link,
                        user_id = excluded.user_id,
                        metadata_json = excluded.metadata_json,
                        created_at = excluded.created_at,
                        expires_at = excluded.expires_at
                    """,
                    (link_id, link, user_id, metadata_json, now, expires_at),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def retrieve_link(
        self, link_id: str, user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Retrieve an unexpired link, optionally enforcing its owner."""
        now = time.time()
        with self._lock, closing(self._connect()) as connection:
            connection.execute(
                "DELETE FROM pending_links WHERE expires_at < ?", (now,)
            )
            if user_id is None:
                row = connection.execute(
                    """
                    SELECT link, user_id, metadata_json, created_at, expires_at
                    FROM pending_links
                    WHERE link_id = ? AND expires_at >= ?
                    """,
                    (link_id, now),
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT link, user_id, metadata_json, created_at, expires_at
                    FROM pending_links
                    WHERE link_id = ? AND user_id = ? AND expires_at >= ?
                    """,
                    (link_id, user_id, now),
                ).fetchone()

        return self._deserialize_link(row) if row is not None else None

    def consume_link(self, link_id: str, user_id: int) -> Optional[Dict]:
        """Atomically retrieve and delete a link for its owner exactly once."""
        now = time.time()
        with self._lock, closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    "DELETE FROM pending_links WHERE expires_at < ?", (now,)
                )
                row = connection.execute(
                    """
                    SELECT link, user_id, metadata_json, created_at, expires_at
                    FROM pending_links
                    WHERE link_id = ? AND user_id = ? AND expires_at >= ?
                    """,
                    (link_id, user_id, now),
                ).fetchone()

                if row is None:
                    connection.commit()
                    return None

                deleted = connection.execute(
                    "DELETE FROM pending_links WHERE link_id = ? AND user_id = ?",
                    (link_id, user_id),
                )
                if deleted.rowcount != 1:
                    connection.rollback()
                    return None

                connection.commit()
                return self._deserialize_link(row)
            except Exception:
                connection.rollback()
                raise

    def restore_link(
        self, link_id: str, user_id: int, link_data: Dict
    ) -> bool:
        """
        Restore a consumed callback without extending its original expiry.

        Returns False when the original TTL has elapsed, the payload belongs to
        another user, or the ID has already been re-created.
        """
        try:
            stored_user_id = int(link_data["user_id"])
            link = str(link_data["link"])
            created_at = float(link_data["created_at"])
            expires_at = float(link_data["expires_at"])
            metadata = link_data.get("metadata", {})
        except (KeyError, TypeError, ValueError):
            logger.warning("Cannot restore incomplete pending-link payload %s", link_id)
            return False

        if stored_user_id != user_id or expires_at < time.time():
            return False

        metadata_json = json.dumps(
            metadata if isinstance(metadata, dict) else {},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        now = time.time()

        with self._lock, closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    "DELETE FROM pending_links WHERE expires_at < ?", (now,)
                )
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO pending_links (
                        link_id, link, user_id, metadata_json, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        link_id,
                        link,
                        user_id,
                        metadata_json,
                        created_at,
                        expires_at,
                    ),
                )
                connection.commit()
                return cursor.rowcount == 1
            except Exception:
                connection.rollback()
                raise

    @staticmethod
    def _deserialize_link(row: sqlite3.Row) -> Dict:
        """Convert a database row to the legacy LinkStore dictionary shape."""
        try:
            metadata = json.loads(row["metadata_json"])
        except (TypeError, json.JSONDecodeError):
            logger.warning("Invalid metadata JSON in pending-link database")
            metadata = {}

        return {
            "link": row["link"],
            "user_id": row["user_id"],
            "metadata": metadata if isinstance(metadata, dict) else {},
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
        }

    def cleanup_expired(self) -> int:
        """Delete expired callback links and return the number of removed rows."""
        now = time.time()
        with self._lock, closing(self._connect()) as connection:
            cursor = connection.execute(
                "DELETE FROM pending_links WHERE expires_at < ?", (now,)
            )
            return cursor.rowcount

    def _cleanup_expired(self) -> None:
        """Backward-compatible cleanup method."""
        self.cleanup_expired()


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

        metadata.setdefault("url", canonical_url)
        metadata.setdefault("external_urls", {})
        if isinstance(metadata["external_urls"], dict):
            metadata["external_urls"].setdefault("spotify", canonical_url)

        if not config.enable_authorized_audio_delivery:
            response_text = messages.get("metadata_only")
            metadata_text = format_metadata_html(
                metadata,
                link_label=messages.get("open_on_spotify"),
            )
            if metadata_text:
                response_text += f"\n\n{metadata_text}"
            bot.reply_to(message, response_text, parse_mode="HTML")
            return

        # Persist the callback payload before showing a quality keyboard.
        # Do not expose buttons that cannot be consumed after a restart.
        link_id = link_store.generate_link_id(canonical_url, user_id)
        try:
            link_store.store_link(link_id, canonical_url, user_id, metadata)
        except Exception:
            logger.exception("Could not persist pending Spotify link for user %s", user_id)
            bot.reply_to(message, messages.get("unexpected_error"))
            return

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
        metadata_text = format_metadata_html(
            metadata,
            link_label=messages.get("open_on_spotify"),
        )
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


def restore_stored_link_data(
    link_id: str, user_id: int, link_data: Dict
) -> bool:
    """Restore a consumed callback after worker-start failure, preserving its TTL."""
    return link_store.restore_link(link_id, user_id, link_data)


def format_metadata_html(
    metadata: Dict, link_label: str = "Open on Spotify"
) -> str:
    """Render an attributed metadata preview with a direct Spotify link."""
    lines = []
    if metadata.get("valid") and metadata.get("title"):
        title = html.escape(str(metadata.get("title") or "Unknown"))
        lines.append(f"🎵 <b>{title}</b>")
        artist = metadata.get("artist")
        if artist:
            lines.append(f"👤 {html.escape(str(artist))}")

    spotify_url = metadata.get("url") or (metadata.get("external_urls") or {}).get(
        "spotify"
    )
    if spotify_url:
        safe_url = html.escape(str(spotify_url), quote=True)
        safe_label = html.escape(str(link_label))
        lines.append(f'🔗 <a href="{safe_url}">{safe_label}</a>')

    return "\n".join(lines)
