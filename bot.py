"""
Main bot entry point for Spotify Bot.

This module initializes and runs the Telegram bot with all handlers.
"""

import sys
import os
import signal
import threading
import time

from telebot import TeleBot

# Import configuration and logging
from config import config, BOT_TOKEN
from utils.logging_config import setup_logging
from utils.rate_limiter import cleanup_expired_rate_limits

# Import all handlers
from handlers.command_handler import register_command_handlers
from handlers.spotify_handler import register_spotify_handler
from handlers.callback_handler import register_callback_handlers

# Setup logging
logger = setup_logging(__name__)


class SpotifyBot:
    """
    Main Spotify Bot class with improved error handling and lifecycle management.
    """

    def __init__(self, token: str):
        """
        Initialize the bot.

        Args:
            token: Telegram bot token
        """
        self.token = token
        self.bot = None
        self.cleanup_thread = None
        self.running = False

    def _setup_handlers(self):
        """Set up all bot handlers."""
        logger.info("Setting up bot handlers...")

        # Register all handlers
        register_command_handlers(self.bot)
        register_spotify_handler(self.bot)
        register_callback_handlers(self.bot)

        logger.info("All handlers registered successfully")

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""

        def cleanup_worker():
            """Background worker for periodic cleanup tasks."""
            while self.running:
                try:
                    # Clean up expired rate limits every 5 minutes
                    cleanup_expired_rate_limits()
                    logger.debug("Performed periodic cleanup")
                except Exception as e:
                    logger.error("Error in cleanup worker: %s", e)

                # Wait 5 minutes
                for _ in range(300):  # 5 minutes in seconds
                    if not self.running:
                        break
                    time.sleep(1)

        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        logger.info("Background cleanup thread started")

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info("Received signal %s, shutting down gracefully...", signum)
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def start(self):
        """Start the bot."""
        try:
            # Initialize bot
            self.bot = TeleBot(self.token)
            logger.info("Bot initialized successfully")

            # Set up handlers
            self._setup_handlers()

            # Set up signal handlers
            self._setup_signal_handlers()

            # Start background cleanup
            self.running = True
            self._start_cleanup_thread()

            # Log bot info
            bot_info = self.bot.get_me()
            logger.info("Starting bot: @%s (%s)", bot_info.username, bot_info.first_name)

            # Log configuration
            logger.info("Configuration:")
            logger.info(
                "  - Rate limit: %d requests per %ds", config.rate_limit_requests, config.rate_limit_window_seconds
            )
            logger.info("  - Default quality: %dkbps", config.default_quality)
            logger.info("  - Max file size: %dMB", config.max_download_size_mb)
            logger.info(
                "  - Supported languages: %s", ', '.join(config.supported_languages)
            )

            # Start polling
            logger.info("Bot is running... Press Ctrl+C to stop.")
            self.bot.infinity_polling(
                timeout=20, long_polling_timeout=20, none_stop=True, interval=1
            )

        except Exception as e:
            logger.error("Error starting bot: %s", e)
            self.stop()
            raise

    def stop(self):
        """Stop the bot gracefully."""
        logger.info("Stopping bot...")

        self.running = False

        if self.bot:
            try:
                self.bot.stop_polling()
            except Exception as e:
                logger.error("Error stopping bot polling: %s", e)

        if self.cleanup_thread and self.cleanup_thread.is_alive():
            logger.info("Waiting for cleanup thread to finish...")
            self.cleanup_thread.join(timeout=5)

        logger.info("Bot stopped successfully")


def main():
    """Main entry point."""
    logger.info("Starting Spotify Bot...")
    logger.info("Python version: %s", sys.version)
    logger.info("Working directory: %s", os.getcwd())

    # Validate token
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is required")
        return 1

    try:
        # Create and start bot
        spotify_bot = SpotifyBot(BOT_TOKEN)
        spotify_bot.start()

    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        return 0
    except Exception as e:
        logger.error("Fatal error: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
