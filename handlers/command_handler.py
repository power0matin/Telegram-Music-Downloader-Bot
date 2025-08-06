"""
Command handler for Spotify Bot.

This module handles bot commands like /start, /help with multilingual support.
"""

from telebot import TeleBot
from telebot.types import Message

from utils.logging_config import setup_logging, log_user_action
from utils.i18n import get_messages
from config import config

logger = setup_logging(__name__)


def register_command_handlers(bot: TeleBot):
    """
    Register all command handlers.

    Args:
        bot: Telegram bot instance
    """

    @bot.message_handler(commands=["start"])
    def handle_start_command(message: Message):
        """Handle /start command."""
        user_id = message.from_user.id
        chat_id = message.chat.id

        log_user_action(logger, user_id, "Start command", f"Chat: {chat_id}")

        messages = get_messages(user_id)

        # Send welcome message
        bot.send_message(chat_id, messages.get("welcome"))

    @bot.message_handler(commands=["help"])
    def handle_help_command(message: Message):
        """Handle /help command."""
        user_id = message.from_user.id
        chat_id = message.chat.id

        log_user_action(logger, user_id, "Help command", f"Chat: {chat_id}")

        messages = get_messages(user_id)

        # Send help message
        bot.send_message(chat_id, messages.get("help"), parse_mode="Markdown")
