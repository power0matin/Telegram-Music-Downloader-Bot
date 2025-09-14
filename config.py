from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Config:
    """Application configuration with sensible defaults.

    Values can be overridden via environment variables. This module provides a
    lightweight replacement for the original project configuration which was
    missing from the repository. Having defaults allows the utility modules and
    tests to import :data:`config` without raising ``ModuleNotFoundError``.
    """

    download_dir: str = os.getenv("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", 5))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60))
    default_quality: int = int(os.getenv("DEFAULT_QUALITY", 320))
    max_download_size_mb: int = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", 50))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    supported_languages: Tuple[str, ...] = ("en", "fa")

config = Config()

# Bot token and queue path are exposed at module level for backwards
# compatibility with existing imports throughout the codebase.
BOT_TOKEN = os.getenv("BOT_TOKEN", "TEST_TOKEN")
QUEUE_PATH = os.getenv("QUEUE_PATH", os.path.join(os.getcwd(), "queue", "queue.json"))

__all__ = ["config", "BOT_TOKEN", "QUEUE_PATH", "Config"]
