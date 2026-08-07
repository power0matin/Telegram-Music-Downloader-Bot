from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path

from dotenv import load_dotenv

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


def _require_range(name: str, value: int, minimum: int, maximum: int) -> int:
    """Validate an integer configuration value against an inclusive range."""
    if not minimum <= value <= maximum:
        raise RuntimeError(
            f"Invalid value for {name}: {value!r}. "
            f"Must be between {minimum} and {maximum}."
        )
    return value


def _resolve_project_path(value: str) -> Path:
    """Resolve relative runtime paths against the repository, not process CWD."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (BASE_DIR / path).resolve()


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
    download_timeout_seconds: int
    upload_timeout_seconds: int
    upload_retries: int
    max_concurrent_downloads: int

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
        download_dir = _resolve_project_path(
            _get_str("DOWNLOAD_DIR", str(BASE_DIR / "downloads"))
        )
        queue_path = _resolve_project_path(
            _get_str("QUEUE_PATH", str(BASE_DIR / "queue" / "queue.json"))
        )

        # Download / quality limits
        default_quality = _get_int("DEFAULT_QUALITY", 320)
        if default_quality not in (128, 320):
            raise RuntimeError(
                "Invalid value for DEFAULT_QUALITY. Supported values are 128 and 320."
            )

        # Telegram's hosted Bot API currently accepts audio uploads up to 50 MB.
        # Reject impossible configurations up front instead of downloading files
        # that can never be delivered to the user.
        max_download_size_mb = _require_range(
            "MAX_DOWNLOAD_SIZE_MB", _get_int("MAX_DOWNLOAD_SIZE_MB", 50), 1, 50
        )
        download_timeout_seconds = _require_range(
            "DOWNLOAD_TIMEOUT_SECONDS",
            _get_int("DOWNLOAD_TIMEOUT_SECONDS", 900),
            60,
            7200,
        )
        upload_timeout_seconds = _require_range(
            "UPLOAD_TIMEOUT_SECONDS",
            _get_int("UPLOAD_TIMEOUT_SECONDS", 180),
            30,
            900,
        )
        upload_retries = _require_range(
            "UPLOAD_RETRIES", _get_int("UPLOAD_RETRIES", 3), 1, 5
        )
        max_concurrent_downloads = _require_range(
            "MAX_CONCURRENT_DOWNLOADS",
            _get_int("MAX_CONCURRENT_DOWNLOADS", 3),
            1,
            10,
        )

        # Rate limiter
        rate_limit_requests = _get_int("RATE_LIMIT_REQUESTS", 20)
        rate_limit_window_seconds = _get_int("RATE_LIMIT_WINDOW_SECONDS", 60)

        # yt-dlp / spotdl reliability options
        # COOKIE_FILE: path to a cookies.txt exported from a logged-in YouTube
        # session (Netscape format). Strongly recommended on VPS/datacenter IPs,
        # since YouTube frequently blocks anonymous requests from cloud providers.
        cookie_file_raw = _get_str("COOKIE_FILE", "")
        cookie_file = (
            str(_resolve_project_path(cookie_file_raw)) if cookie_file_raw else ""
        )
        # YTDLP_EXTRA_ARGS: raw extra args passed through to yt-dlp via spotdl's
        # --yt-dlp-args, e.g. "--extractor-args youtube:player_client=web_music,default --sleep-requests 1"
        ytdlp_extra_args = _get_str("YTDLP_EXTRA_ARGS", "")
        # PROXY_URL: route yt-dlp's YouTube requests through a proxy with a
        # cleaner IP reputation than the VPS's own (datacenter IPs get bot-
        # blocked by YouTube much more aggressively than residential ones).
        # This is the "no manual cookies" fix — set it and forget it.
        proxy_url = _get_str("PROXY_URL", "")

        # AUDIO_PROVIDERS: comma-separated fallback order for spotdl's audio
        # sources. SoundCloud-first reduces dependence on YouTube from common
        # datacenter IPs; YouTube Music and YouTube remain fallbacks.
        audio_providers_raw = _get_str(
            "AUDIO_PROVIDERS", "soundcloud,youtube-music,youtube"
        )
        audio_providers: Tuple[str, ...] = tuple(
            p.strip() for p in audio_providers_raw.split(",") if p.strip()
        )
        supported_audio_providers = {
            "youtube",
            "youtube-music",
            "soundcloud",
            "bandcamp",
            "piped",
        }
        invalid_providers = [
            provider
            for provider in audio_providers
            if provider not in supported_audio_providers
        ]
        if invalid_providers:
            raise RuntimeError(
                "Invalid AUDIO_PROVIDERS value(s): "
                + ", ".join(invalid_providers)
                + ". Supported values: "
                + ", ".join(sorted(supported_audio_providers))
            )
        if not audio_providers:
            raise RuntimeError("AUDIO_PROVIDERS must contain at least one provider.")

        # Logging
        log_level = _get_str("LOG_LEVEL", "INFO").upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise RuntimeError(
                "Invalid LOG_LEVEL. Use DEBUG, INFO, WARNING, ERROR, or CRITICAL."
            )

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
            download_timeout_seconds=download_timeout_seconds,
            upload_timeout_seconds=upload_timeout_seconds,
            upload_retries=upload_retries,
            max_concurrent_downloads=max_concurrent_downloads,
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

# Keep QUEUE_PATH as a plain string for old code that imports it directly
QUEUE_PATH = str(config.queue_path)

__all__ = ["config", "BOT_TOKEN", "QUEUE_PATH", "Config"]
