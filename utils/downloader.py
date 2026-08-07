"""
Enhanced downloader module for Spotify Bot.

This module handles downloading music from Spotify links using spotdl,
with improved error handling, progress updates, and metadata extraction.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from telebot import TeleBot
from telebot.types import Message

from config import config
from utils.logging_config import (
    setup_logging,
    log_download_attempt,
    log_download_success,
    log_download_error,
)
from utils.spotify_utils import get_spotify_metadata, validate_spotify_url
from utils.i18n import get_messages

logger = setup_logging(__name__)


@dataclass
class DownloadResult:
    """Result of a download operation."""

    success: bool
    files: Optional[List[str]] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    total_size: int = 0
    download_dir: Optional[str] = None


class DownloadError(Exception):
    """Custom exception for download errors."""

    pass


class DependencyError(DownloadError):
    """Raised when required dependencies are missing."""

    pass


class SpotifyDownloader:
    """
    Enhanced Spotify downloader with better error handling and features.
    """

    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize the downloader.

        Args:
            download_dir: Base download directory (uses config default if None)
        """
        self.download_dir = download_dir or config.download_dir
        self.max_file_size = (
            config.max_download_size_mb * 1024 * 1024
        )  # Convert to bytes

        # Ensure download directory exists
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)

    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required dependencies are installed.

        Returns:
            Dictionary with dependency status
        """
        dependencies = {
            "spotdl": self._is_spotdl_installed(),
            "ffmpeg": self._is_ffmpeg_installed(),
        }

        logger.debug("Dependency check: %s", dependencies)
        return dependencies

    def _is_spotdl_installed(self) -> bool:
        """Check if spotdl is installed."""
        try:
            result = subprocess.run(
                ["spotdl", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _is_ffmpeg_installed(self) -> bool:
        """Check if FFmpeg is installed."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _get_user_download_dir(self, user_id: int) -> str:
        """
        Get user-specific download directory.

        Args:
            user_id: Telegram user ID

        Returns:
            Path to user's download directory
        """
        user_dir = os.path.join(self.download_dir, str(user_id))
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        return user_dir

    def _create_request_download_dir(self, user_id: int) -> str:
        """Create an isolated directory for one download request."""
        user_dir = self._get_user_download_dir(user_id)
        return tempfile.mkdtemp(prefix="request-", dir=user_dir)

    def _prepare_download_command(
        self, spotify_url: str, output_dir: str, quality: int
    ) -> List[str]:
        """
        Prepare the spotdl download command.

        Args:
            spotify_url: Spotify URL to download
            output_dir: Output directory (per-user)
            quality: Audio quality (128 or 320)

        Returns:
            List of command arguments
        """
        # Validate and sanitize quality
        if quality not in [128, 320]:
            quality = config.default_quality

        # spotdl expects values like 128k, 320k
        bitrate = f"{quality}k"

        # downloads/USER_ID/Artist - Title.mp3
        output_template = os.path.join(
            output_dir,
            "{artists} - {title}.{output-ext}",
        )

        # Build a spotDL 4.5.x command. Keep the query before --audio because
        # --audio accepts a variable number of provider values and would
        # otherwise consume a trailing URL.
        command = [
            "spotdl",
            "download",
            spotify_url,
            "--bitrate",
            bitrate,
            "--format",
            "mp3",
            "--output",
            output_template,
            "--overwrite",
            "skip",  # Skip if file already exists
            "--max-filename-length",
            "180",
        ]

        # Fall back through the configured audio sources in order.
        if config.audio_providers:
            command += ["--audio", *config.audio_providers]

        # Use cookies from a real logged-in browser session, if provided.
        # Optional — see PROXY_URL below for a cookie-free alternative.
        if config.cookie_file:
            command += ["--cookie-file", config.cookie_file]

        # Optional proxy for provider requests on networks where a source is
        # blocked or heavily rate-limited.
        if config.proxy_url:
            command += ["--proxy", config.proxy_url]

        # Any extra raw yt-dlp args (extractor-args, sleep-requests, etc.)
        if config.ytdlp_extra_args:
            command += ["--yt-dlp-args", config.ytdlp_extra_args]

        return command

    @staticmethod
    def _redact_command(command: List[str]) -> str:
        """Render a command for logs without proxy/cookie/yt-dlp secrets."""
        redacted: List[str] = []
        redact_next = False
        sensitive_options = {"--proxy", "--cookie-file", "--yt-dlp-args"}
        for part in command:
            if redact_next:
                redacted.append("<redacted>")
                redact_next = False
                continue
            redacted.append(part)
            if part in sensitive_options:
                redact_next = True
        return " ".join(redacted)

    @staticmethod
    def _redact_output(text: str) -> str:
        """Remove configured credentials/arguments from captured process output."""
        redacted = text
        for sensitive_value in (config.proxy_url, config.ytdlp_extra_args):
            if sensitive_value:
                redacted = redacted.replace(sensitive_value, "<redacted>")
        return redacted

    def _execute_download(
        self, command: List[str], timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """
        Execute the download command with proper error handling.

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            Completed process result

        Raises:
            DownloadError: If download fails
        """
        max_retries = 3
        retry_delay = 5
        effective_timeout = timeout or config.download_timeout_seconds

        for attempt in range(max_retries):
            try:
                logger.debug(
                    "Download attempt %s/%s - command: %s",
                    attempt + 1,
                    max_retries,
                    self._redact_command(command),
                )

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=effective_timeout,
                )
            except subprocess.TimeoutExpired as exc:
                if attempt < max_retries - 1:
                    logger.warning(
                        "Download timed out after %ss, retrying in %ss",
                        effective_timeout,
                        retry_delay,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise DownloadError("Download timed out after multiple attempts") from exc
            except OSError as exc:
                raise DownloadError(f"Failed to start spotDL: {exc}") from exc

            stdout = result.stdout or ""
            stderr = result.stderr or ""
            combined = (stdout + "\n" + stderr).lower()

            logger.debug(
                "spotDL exit code=%s\n--- stdout ---\n%s\n--- stderr ---\n%s",
                result.returncode,
                self._redact_output(stdout[:4000]),
                self._redact_output(stderr[:4000]),
            )

            # spotDL may report individual provider failures while still
            # successfully downloading other songs in an album/playlist. A zero
            # exit code is therefore allowed through and the produced files are
            # treated as the source of truth.
            if result.returncode == 0:
                return result

            error_message, retryable = self._classify_download_error(
                combined, stdout, stderr
            )
            if retryable and attempt < max_retries - 1:
                logger.warning(
                    "%s; retrying in %ss (attempt %s/%s)",
                    error_message,
                    retry_delay,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(retry_delay)
                retry_delay *= 2
                continue

            raise DownloadError(error_message)

        raise DownloadError("Download failed after all retry attempts")

    @staticmethod
    def _classify_download_error(
        combined: str, stdout: str, stderr: str
    ) -> tuple[str, bool]:
        """Map spotDL output to a stable user-facing failure and retry policy."""
        if "unrecognized arguments" in combined or "invalid choice" in combined:
            return "Installed spotDL version is incompatible with this bot", False
        if "invalid base62 id" in combined or "invalid spotify" in combined:
            return "Invalid Spotify track id", False
        if "no results found" in combined or "track not found" in combined:
            return "Track not found on Spotify", False
        if "unavailable" in combined and "audio" not in combined:
            return "Track is unavailable in your region", False
        if "sign in to confirm" in combined or "please sign in" in combined:
            return "YouTube requires sign-in - set COOKIE_FILE in .env", False
        if (
            "rate limit" in combined
            or "rate/request limit" in combined
            or "too many requests" in combined
            or "status code: 429" in combined
        ):
            return "Rate limited by audio source", True
        if (
            "audioprovidererror" in combined
            or "yt-dlp download error" in combined
            or "could not extract" in combined
        ):
            return "Audio provider error - all configured sources failed", True
        if (
            "network" in combined
            or "connection reset" in combined
            or "connection aborted" in combined
            or "temporary failure" in combined
        ):
            return "Network connection error", True

        detail = (stderr.strip() or stdout.strip() or "unknown spotDL error")[:300]
        detail = SpotifyDownloader._redact_output(detail)
        logger.error("Unhandled spotDL error: %s", detail)
        return f"Download failed: {detail}", False

    def _process_downloaded_files(self, download_dir: str) -> List[Dict[str, Any]]:
        """
        Process downloaded files and extract information.

        Args:
            download_dir: Directory containing downloaded files

        Returns:
            List of file information dictionaries
        """
        files: List[Dict[str, Any]] = []

        # Telegram's sendAudio endpoint accepts MP3 and M4A uploads.
        allowed_exts = (".mp3", ".m4a")

        try:
            if not os.path.isdir(download_dir):
                logger.warning(
                    "Download directory does not exist or is not a directory: %s", download_dir
                )
                return []

            # spotDL may create nested directories for lists, so walk recursively.
            for root, _, filenames in os.walk(download_dir):
                for filename in filenames:
                    if not filename.lower().endswith(allowed_exts):
                        continue

                    file_path = os.path.join(root, filename)

                    try:
                        file_stat = os.stat(file_path)
                    except OSError as e:
                        logger.warning("Skipping file %s: %s", file_path, e)
                        continue

                    # Ignore incomplete/empty output files.
                    if file_stat.st_size == 0:
                        logger.warning("Skipping zero-size file %s", filename)
                        continue

                    # Files larger than the configured Telegram delivery limit
                    # cannot be sent through the hosted Bot API.
                    if file_stat.st_size > self.max_file_size:
                        logger.warning("File %s exceeds size limit", filename)
                        continue

                    file_info = {
                        "filename": filename,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "size_mb": file_stat.st_size / (1024 * 1024),
                    }

                    files.append(file_info)
                    logger.debug(
                        "Processed file: %s (%.2fMB)", filename, file_info['size_mb']
                    )

            if not files:
                try:
                    top_level = os.listdir(download_dir)
                except Exception:
                    top_level = "unavailable"

                logger.warning(
                    "No audio files found under %s. Top-level contents: %s", download_dir, top_level
                )

            return files

        except Exception as e:
            logger.error("Error processing downloaded files: %s", e)
            raise DownloadError(f"Error processing downloaded files: {e}")

    def _has_oversized_audio(self, download_dir: str) -> bool:
        """Return whether spotDL produced audio that Telegram cannot accept."""
        for root, _, filenames in os.walk(download_dir):
            for filename in filenames:
                if not filename.lower().endswith((".mp3", ".m4a")):
                    continue
                try:
                    if os.path.getsize(os.path.join(root, filename)) > self.max_file_size:
                        return True
                except OSError:
                    continue
        return False

    def download(
        self, spotify_url: str, user_id: int, quality: Optional[int] = None
    ) -> DownloadResult:
        """
        Download music from Spotify URL.

        Args:
            spotify_url: Spotify URL to download
            user_id: Telegram user ID
            quality: Audio quality (128 or 320)

        Returns:
            DownloadResult with download information

        Raises:
            DownloadError: If download fails
            DependencyError: If required tools are missing
        """
        if quality is None:
            quality = config.default_quality

        # Validate URL
        if not validate_spotify_url(spotify_url):
            raise DownloadError("Invalid Spotify URL")

        # Check dependencies
        deps = self.check_dependencies()
        if not deps["spotdl"]:
            raise DependencyError("spotdl is not installed")

        if not deps["ffmpeg"]:
            raise DependencyError("ffmpeg is not installed")

        # Get metadata
        metadata = get_spotify_metadata(spotify_url)

        # Each request gets its own workspace. Sharing one user directory across
        # concurrent callbacks can mix tracks and lets one request delete files
        # belonging to another request.
        request_download_dir = self._create_request_download_dir(user_id)
        command = self._prepare_download_command(
            spotify_url, request_download_dir, quality
        )

        # Log download attempt
        log_download_attempt(logger, user_id, spotify_url, quality)

        execution_error: Optional[DownloadError] = None
        execution_result: Optional[subprocess.CompletedProcess] = None
        try:
            try:
                execution_result = self._execute_download(command)
            except DownloadError as exc:
                # For albums/playlists spotDL may have produced valid files before
                # a later item failed. Deliver those files instead of discarding
                # the whole request.
                execution_error = exc

            files = self._process_downloaded_files(request_download_dir)

            if not files:
                if self._has_oversized_audio(request_download_dir):
                    raise DownloadError(
                        "Downloaded audio exceeds the configured Telegram upload size limit"
                    )
                if execution_error is not None:
                    raise execution_error
                if execution_result is not None:
                    stdout = execution_result.stdout or ""
                    stderr = execution_result.stderr or ""
                    combined = (stdout + "\n" + stderr).lower()
                    known_failure_markers = (
                        "audioprovidererror",
                        "yt-dlp download error",
                        "no results found",
                        "track not found",
                        "invalid base62 id",
                        "sign in to confirm",
                        "rate limit",
                        "too many requests",
                    )
                    if any(marker in combined for marker in known_failure_markers):
                        error_message, _ = self._classify_download_error(
                            combined, stdout, stderr
                        )
                        raise DownloadError(error_message)
                raise DownloadError("No files were downloaded")

            # Calculate total size
            total_size = sum(f["size"] for f in files)

            # Log success
            for file_info in files:
                log_download_success(
                    logger, user_id, file_info["filename"], file_info["size"]
                )

            return DownloadResult(
                success=True,
                files=[f["path"] for f in files],
                warning=str(execution_error) if execution_error else None,
                metadata=metadata,
                total_size=total_size,
                download_dir=request_download_dir,
            )

        except (DownloadError, DependencyError) as e:
            log_download_error(logger, user_id, str(e), spotify_url)
            return DownloadResult(
                success=False,
                error=str(e),
                metadata=metadata,
                download_dir=request_download_dir,
            )


def _send_text(bot: TeleBot, chat_id: int, message: Message, text: str) -> None:
    """Send a status/error message back to the chat that initiated the request."""
    kwargs: Dict[str, Any] = {}
    thread_id = getattr(message, "message_thread_id", None)
    if thread_id is not None:
        kwargs["message_thread_id"] = thread_id
    bot.send_message(chat_id, text, **kwargs)


def _is_retryable_upload_error(exc: Exception) -> bool:
    """Return whether a Telegram upload error looks transient."""
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True

    error_text = str(exc).lower()
    retry_markers = (
        "timed out",
        "timeout",
        "connection aborted",
        "connection reset",
        "remote end closed",
        "temporarily unavailable",
        "bad gateway",
        "service unavailable",
        "gateway timeout",
        "too many requests",
        "retry after",
        "error code: 429",
        " 502",
        " 503",
        " 504",
    )
    return any(marker in error_text for marker in retry_markers)


def _upload_retry_delay(exc: Exception, attempt: int) -> int:
    """Honor Telegram Retry-After hints, otherwise use short exponential backoff."""
    match = re.search(r"retry after\D*(\d+)", str(exc), flags=re.IGNORECASE)
    if match:
        return min(max(int(match.group(1)) + 1, 1), 120)
    return min(2 ** attempt, 8)


def _send_audio_with_retry(
    bot: TeleBot,
    chat_id: int,
    message: Message,
    file_path: str,
    caption: str,
) -> bool:
    """Upload one audio file with a bounded retry for transient network errors."""
    send_kwargs: Dict[str, Any] = {
        "caption": caption,
        "timeout": config.upload_timeout_seconds,
    }
    thread_id = getattr(message, "message_thread_id", None)
    if thread_id is not None:
        send_kwargs["message_thread_id"] = thread_id

    for attempt in range(1, config.upload_retries + 1):
        try:
            # Re-open on every attempt so retries always upload from byte zero.
            with open(file_path, "rb") as audio_file:
                bot.send_audio(chat_id, audio_file, **send_kwargs)
            return True
        except Exception as exc:  # pyTelegramBotAPI wraps several network errors
            retryable = _is_retryable_upload_error(exc)
            if not retryable or attempt >= config.upload_retries:
                logger.error(
                    "Audio upload failed for %s after %s attempt(s): %s",
                    file_path,
                    attempt,
                    exc,
                )
                return False

            delay = _upload_retry_delay(exc, attempt)
            logger.warning(
                "Transient Telegram upload error for %s: %s; retrying in %ss",
                file_path,
                exc,
                delay,
            )
            time.sleep(delay)

    return False


def _build_audio_caption(messages, result: DownloadResult, file_path: str) -> str:
    """Build a useful caption without applying list-level metadata to every track."""
    filename = os.path.basename(file_path)
    metadata = result.metadata or {}
    if metadata.get("valid") and metadata.get("type") == "track":
        title = metadata.get("title")
        artist = metadata.get("artist")
        if title and artist:
            caption = f"🎵 {title}\n👤 {artist}"
            if metadata.get("album"):
                caption += f"\n💿 {metadata['album']}"
            return caption
    return messages.get("download_complete", filename=filename)


def download_and_send(
    bot: TeleBot,
    message: Message,
    spotify_url: str,
    quality: int,
    user_id: Optional[int] = None,
) -> None:
    """
    Download Spotify track and send to user with enhanced error handling.

    Args:
        bot: Telegram bot instance
        message: User message
        spotify_url: Spotify URL to download
        quality: Audio quality
        user_id: Telegram user ID used for rate limits, language and isolation.
    """
    chat_id = message.chat.id
    if user_id is None:
        user_id = chat_id
    messages = get_messages(user_id)

    downloader = SpotifyDownloader()
    result: Optional[DownloadResult] = None

    try:
        deps = downloader.check_dependencies()

        if not deps["spotdl"]:
            _send_text(bot, chat_id, message, messages.get("spotdl_not_installed"))
            return

        if not deps["ffmpeg"]:
            _send_text(bot, chat_id, message, messages.get("ffmpeg_not_installed"))
            return

        result = downloader.download(spotify_url, user_id, quality)

        if not result.success:
            error_text = (result.error or "").lower()

            if "rate limit" in error_text:
                error_message = messages.get("retry_failed")
            elif "incompatible" in error_text:
                error_message = messages.get("spotdl_incompatible")
            elif (
                "audio provider" in error_text
                or "yt-dlp" in error_text
                or "blocked" in error_text
            ):
                error_message = messages.get("audio_source_unavailable")
            elif "sign-in" in error_text or "sign in" in error_text:
                error_message = messages.get("youtube_signin_required")
            elif (
                "invalid spotify track id" in error_text
                or "invalid spotify url" in error_text
            ):
                error_message = messages.get("invalid_url")
            elif "track not found" in error_text:
                error_message = messages.get("track_not_found")
            elif "unavailable" in error_text:
                error_message = messages.get("track_unavailable")
            elif "size limit" in error_text or "too large" in error_text:
                error_message = messages.get(
                    "file_too_large", limit=config.max_download_size_mb
                )
            elif "not found" in error_text or "no files" in error_text:
                error_message = messages.get("no_files_downloaded")
            elif "timed out" in error_text:
                error_message = messages.get("download_timeout")
            else:
                error_message = messages.get("unexpected_error")

            _send_text(bot, chat_id, message, error_message)
            return

        files_sent = 0
        files_failed = 0
        for file_path in result.files or []:
            caption = _build_audio_caption(messages, result, file_path)
            if _send_audio_with_retry(bot, chat_id, message, file_path, caption):
                files_sent += 1
            else:
                files_failed += 1

        if files_sent == 0:
            _send_text(bot, chat_id, message, messages.get("file_send_error"))
        elif files_failed or result.warning:
            _send_text(
                bot,
                chat_id,
                message,
                messages.get(
                    "partial_download",
                    sent=files_sent,
                    failed=files_failed,
                ),
            )

    except Exception as e:
        logger.error("Unexpected error in download_and_send: %s", e, exc_info=True)
        try:
            _send_text(bot, chat_id, message, messages.get("unexpected_error"))
        except Exception:
            logger.exception("Failed to report download error to chat %s", chat_id)
    finally:
        if result and result.download_dir:
            shutil.rmtree(result.download_dir, ignore_errors=True)

        # Remove the per-user parent if no request directories remain. Never
        # create the directory during cleanup.
        user_dir = os.path.join(str(downloader.download_dir), str(user_id))
        try:
            os.rmdir(user_dir)
        except OSError:
            pass
