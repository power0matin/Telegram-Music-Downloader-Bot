"""
Logging configuration for Spotify Bot.

This module sets up structured logging with proper formatters and handlers.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import config


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        name: Logger name. If None, uses root logger.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Set log level from config
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    try:
        log_dir = os.path.join(os.path.dirname(config.download_dir), "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "spotify_bot.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("Could not set up file logging: %s", e)

    return logger


def log_user_action(
    logger: logging.Logger, user_id: int, action: str, details: str = ""
):
    """
    Log user actions with consistent formatting.

    Args:
        logger: Logger instance
        user_id: Telegram user ID
        action: Action performed
        details: Additional details
    """
    message = f"User {user_id} - {action}"
    if details:
        message += f" - {details}"
    logger.info(message)


def log_download_attempt(
    logger: logging.Logger, user_id: int, spotify_url: str, quality: int
):
    """
    Log download attempts.

    Args:
        logger: Logger instance
        user_id: Telegram user ID
        spotify_url: Spotify URL being downloaded
        quality: Audio quality
    """
    log_user_action(
        logger,
        user_id,
        "Download attempt",
        f"URL: {spotify_url[:50]}... Quality: {quality}kbps",
    )


def log_download_success(
    logger: logging.Logger, user_id: int, filename: str, file_size: int
):
    """
    Log successful downloads.

    Args:
        logger: Logger instance
        user_id: Telegram user ID
        filename: Downloaded filename
        file_size: File size in bytes
    """
    size_mb = file_size / (1024 * 1024)
    log_user_action(
        logger, user_id, "Download success", f"File: {filename} Size: {size_mb:.2f}MB"
    )


def log_download_error(
    logger: logging.Logger, user_id: int, error: str, spotify_url: str
):
    """
    Log download errors.

    Args:
        logger: Logger instance
        user_id: Telegram user ID
        error: Error message
        spotify_url: Spotify URL that failed
    """
    log_user_action(
        logger, user_id, "Download error", f"Error: {error} URL: {spotify_url[:50]}..."
    )
