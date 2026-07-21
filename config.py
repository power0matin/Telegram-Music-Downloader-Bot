from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path

from dotenv import load_dotenv  # make sure python-dotenv is installed

# Base directory of the project (where config.py and .env live)
BASE_DIR = Path(__file__).resolve().parent

# Load .env from project root if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    # override=False → if a var already exists in the environment, keep it
    load_dotenv(dotenv_path=ENV_PATH, override=False)


def _get_str(name: str, default: str) -> str:
    """
    Read a string env var, trim spaces, and fall back to default if empty.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip()
    return value or default


def _get_int(name: str, default: int) -> int:
    """
    Read an integer env var and validate it as a positive integer.
    If not set, return default. If invalid, fail fast with a clear error.
    """
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default

    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(
            f"Invalid value for {name}: {raw!r}. Must be a positive integer."
        )

    if value <= 0:
        raise RuntimeError(
            f"Invalid value for {name}: {raw!r}. Must be a positive integer."
        )

    return value


@dataclass(frozen=True)
class Config:
    """
    Central configuration object for the Telegram Music Downloader Bot.

    Values are primarily loaded from environment variables (including .env),
    with sane defaults for development.
    """

    download_dir: Path
    queue_path: Path

    default_quality: int
    max_download_size_mb: int

    log_level: str
    default_language: str

    # rate limiter config (used by utils.rate_limiter.RateLimiter)
    rate_limit_requests: int
    rate_limit_window_seconds: int

    # yt-dlp / spotdl reliability options (help avoid YouTube bot-blocking on VPS IPs)
    cookie_file: str
    ytdlp_extra_args: str
    proxy_url: str
    audio_providers: Tuple[str, ...] = ("soundcloud", "youtube-music", "youtube")

    supported_languages: Tuple[str, ...] = ("en", "fa")

    @classmethod
    def from_env(cls) -> "Config":
        """
        Build a Config instance from process environment variables.
        """

        # Paths
        download_dir = Path(_get_str("DOWNLOAD_DIR", str(BASE_DIR / "downloads")))
        queue_path = Path(
            _get_str("QUEUE_PATH", str(BASE_DIR / "queue" / "queue.json"))
        )

        # Download / quality limits
        default_quality = _get_int("DEFAULT_QUALITY", 320)
        max_download_size_mb = _get_int("MAX_DOWNLOAD_SIZE_MB", 50)

        # Rate limiter
        rate_limit_requests = _get_int("RATE_LIMIT_REQUESTS", 20)
        rate_limit_window_seconds = _get_int("RATE_LIMIT_WINDOW_SECONDS", 60)

        # yt-dlp / spotdl reliability options
        # COOKIE_FILE: path to a cookies.txt exported from a logged-in YouTube
        # session (Netscape format). Strongly recommended on VPS/datacenter IPs,
        # since YouTube frequently blocks anonymous requests from cloud providers.
        cookie_file = _get_str("COOKIE_FILE", "")
        # YTDLP_EXTRA_ARGS: raw extra args passed through to yt-dlp via spotdl's
        # --yt-dlp-args, e.g. "--extractor-args youtube:player_client=web_music,default --sleep-requests 1"
        ytdlp_extra_args = _get_str("YTDLP_EXTRA_ARGS", "")
        # PROXY_URL: route yt-dlp's YouTube requests through a proxy with a
        # cleaner IP reputation than the VPS's own (datacenter IPs get bot-
        # blocked by YouTube much more aggressively than residential ones).
        # This is the "no manual cookies" fix — set it and forget it.
        # e.g. http://user:pass@residential-proxy-host:port
        proxy_url = _get_str("PROXY_URL", "")

        # AUDIO_PROVIDERS: comma-separated fallback order for spotdl's audio
        # sources. Default is SoundCloud-first because it has no bot-detection
        # problem at all on a plain VPS — no cookies, no proxy, nothing to
        # maintain. YouTube is kept as a fallback for tracks SoundCloud
        # doesn't have, so you still get it when it happens to work.
        audio_providers_raw = _get_str(
            "AUDIO_PROVIDERS", "soundcloud,youtube-music,youtube"
        )
        audio_providers: Tuple[str, ...] = tuple(
            p.strip() for p in audio_providers_raw.split(",") if p.strip()
        )

        # Logging
        log_level = _get_str("LOG_LEVEL", "DEBUG").upper()

        # Language
        supported_languages: Tuple[str, ...] = ("en", "fa")
        default_language = _get_str("DEFAULT_LANGUAGE", "en").lower()
        if default_language not in supported_languages:
            # fallback to English if invalid language is provided
            default_language = "en"

        # Ensure directories exist
        download_dir.mkdir(parents=True, exist_ok=True)
        queue_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(
            download_dir=download_dir,
            queue_path=queue_path,
            default_quality=default_quality,
            max_download_size_mb=max_download_size_mb,
            log_level=log_level,
            default_language=default_language,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window_seconds=rate_limit_window_seconds,
            cookie_file=cookie_file,
            ytdlp_extra_args=ytdlp_extra_args,
            proxy_url=proxy_url,
            audio_providers=audio_providers,
            supported_languages=supported_languages,
        )


# Build a singleton config instance on import
config = Config.from_env()

# Bot token and queue path are exposed at module level for backwards
# compatibility with existing imports throughout the codebase.

BOT_TOKEN = _get_str("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment variable is required. "
        "Set it in your .env file or as a process environment variable."
    )

# Keep QUEUE_PATH as a plain string for old code that imports it directly
QUEUE_PATH = str(config.queue_path)

__all__ = ["config", "BOT_TOKEN", "QUEUE_PATH", "Config"]