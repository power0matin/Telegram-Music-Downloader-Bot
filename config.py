from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class Config:
    """Application configuration with sensible defaults.

    Values can be overridden via environment variables.
    """

    # Use project directory instead of current working directory
    download_dir: str = os.getenv("DOWNLOAD_DIR", str(BASE_DIR / "downloads"))

    # Other settings (keep your existing ones)
    default_quality: int = int(os.getenv("DEFAULT_QUALITY", "320"))
    max_download_size_mb: int = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", "50"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    supported_languages: Tuple[str, ...] = ("en", "fa")


config = Config()

# Bot token and queue path are exposed at module level for backwards
# compatibility with existing imports throughout the codebase.
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required.")

QUEUE_PATH = os.getenv("QUEUE_PATH", str(BASE_DIR / "queue" / "queue.json"))

__all__ = ["config", "BOT_TOKEN", "QUEUE_PATH", "Config"]
