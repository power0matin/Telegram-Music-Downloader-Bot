"""
Enhanced downloader module for Spotify Bot.

This module handles downloading music from Spotify links using spotdl,
with improved error handling, progress updates, and metadata extraction.
"""

import os
import subprocess
import time
import json
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
    metadata: Optional[Dict[str, Any]] = None
    total_size: int = 0


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

    def __init__(self, download_dir: str = None):
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

    def _install_ffmpeg(self) -> bool:
        """
        Attempt to install FFmpeg on Debian-based Linux systems.

        Returns:
            True if installation successful.

        Raises:
            DependencyError: If installation fails or platform is unsupported.
        """
        import platform

        system = platform.system().lower()
        if system != "linux":
            # Do not try to run apt-get on non-Linux systems
            raise DependencyError(
                "Automatic FFmpeg installation is only supported on Linux. "
                "Please install FFmpeg manually on this server."
            )

        try:
            logger.info("Attempting to install FFmpeg via apt-get...")

            # Update package list
            subprocess.run(["sudo", "apt-get", "update"], check=True, timeout=60)

            # Install FFmpeg
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True, timeout=300
            )

            # Verify installation
            if self._is_ffmpeg_installed():
                logger.info("FFmpeg installed successfully")
                return True

            raise DependencyError("FFmpeg installation verification failed")

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            raise DependencyError(f"Failed to install FFmpeg: {e}")

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

        # Build command for modern spotdl CLI:
        # spotdl --bitrate 320k --format mp3 --output "downloads/UID/{artists} - {title}.{output-ext}" URL
        command = [
            "spotdl",
            "--bitrate",
            bitrate,
            "--format",
            "mp3",
            "--output",
            output_template,
            "--overwrite",
            "skip",  # Skip if file already exists
        ]

        # Fall back through multiple audio sources instead of only youtube-music.
        # If YouTube Music blocks/rate-limits us, spotdl will try youtube, then
        # soundcloud, instead of failing the whole track outright.
        if config.audio_providers:
            command += ["--audio-providers", *config.audio_providers]

        # Use cookies from a real logged-in browser session, if provided.
        # Optional — see PROXY_URL below for a cookie-free alternative.
        if config.cookie_file:
            command += ["--cookie-file", config.cookie_file]

        # Route yt-dlp through a proxy with better IP reputation than the VPS
        # itself. This is the "no manual cookies" fix for
        # "AudioProviderError: YT-DLP download error" on datacenter IPs — set
        # PROXY_URL once and it just keeps working, no re-exporting cookies.
        if config.proxy_url:
            command += ["--proxy", config.proxy_url]

        # Any extra raw yt-dlp args (extractor-args, sleep-requests, etc.)
        if config.ytdlp_extra_args:
            command += ["--yt-dlp-args", config.ytdlp_extra_args]

        command.append(spotify_url)

        return command

    def _execute_download(
        self, command: List[str], timeout: int = 300
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

        for attempt in range(max_retries):
            try:
                logger.debug(
                    "Download attempt %s/%s - command: %s",
                    attempt + 1,
                    max_retries,
                    " ".join(command),
                )

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                stdout = result.stdout or ""
                stderr = result.stderr or ""
                combined = (stdout + "\n" + stderr).lower()

                logger.debug(
                    "spotdl exit code=%s, stdout(first 400)=%r, stderr(first 400)=%r",
                    result.returncode,
                    stdout[:400],
                    stderr[:400],
                )

                # exit code صفر ولی با خطای provider در لاگ
                if result.returncode == 0:
                    if (
                        "audioprovidererror" in combined
                        or "yt-dlp download error" in combined
                    ):
                        raise DownloadError("Audio provider error (YouTube / YT-DLP)")
                    if "invalid base62 id" in combined:
                        raise DownloadError("Invalid Spotify track id")
                    return result

                # از این‌جا به بعد exit code غیر صفر است

                if (
                    "rate limit" in combined
                    or "rate/request limit" in combined
                    or "too many requests" in combined
                    or "status code: 429" in combined
                ):
                    if attempt < max_retries - 1:
                        logger.warning(
                            "Rate limit hit, retrying in %ss (attempt %s/%s)",
                            retry_delay,
                            attempt + 1,
                            max_retries,
                        )
                        # backoff
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise DownloadError("Rate limit exceeded after multiple retries")

                if (
                    "audioprovidererror" in combined
                    or "yt-dlp download error" in combined
                ):
                    raise DownloadError("Audio provider error (YouTube / YT-DLP)")

                if "invalid base62 id" in combined or "invalid id" in combined:
                    raise DownloadError("Invalid Spotify track id")

                if "not found" in combined or "unavailable" in combined:
                    raise DownloadError("Track not found or unavailable")

                if "network" in combined or "connection" in combined:
                    raise DownloadError("Network connection error")

                # fallback
                raise DownloadError(f"Download failed: {stderr or stdout}")

            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    logger.warning("Download timed out, retrying...")
                    continue
                raise DownloadError("Download timed out after multiple attempts")

            except DownloadError as e:
                # Audio provider errors are frequently transient (YouTube
                # throttling/blocking a specific search result or IP), so back
                # off and retry with the same fallback-provider command before
                # giving up. We re-raise the *original* message instead of
                # wrapping it, so downstream error-matching in
                # download_and_send still works correctly.
                if attempt < max_retries - 1:
                    logger.warning(
                        "Download error: %s, retrying in %ss (attempt %s/%s)",
                        e,
                        retry_delay,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning("Unexpected error: %s, retrying...", e)
                    time.sleep(retry_delay)
                    continue
                raise DownloadError(f"Unexpected download error: {e}")

        raise DownloadError("Download failed after all retry attempts")

    def _process_downloaded_files(self, download_dir: str) -> List[Dict[str, Any]]:
        """
        Process downloaded files and extract information.

        Args:
            download_dir: Directory containing downloaded files

        Returns:
            List of file information dictionaries
        """
        files: List[Dict[str, Any]] = []

        # پسوندهایی که قبول می‌کنیم (در عمل باید mp3 باشد، ولی برای سازگاری بیشتر)
        allowed_exts = (".mp3", ".m4a", ".flac", ".opus", ".ogg")

        try:
            if not os.path.isdir(download_dir):
                logger.warning(
                    "Download directory does not exist or is not a directory: %s", download_dir
                )
                return []

            # به صورت ریکرسیو در همه‌ی زیرپوشه‌ها بگرد
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

                    # صفر بایت = خراب / ناقص
                    if file_stat.st_size == 0:
                        logger.warning("Skipping zero-size file %s", filename)
                        continue

                    # چک حداکثر سایز
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

    def download(
        self, spotify_url: str, user_id: int, quality: int = None
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
            logger.warning("FFmpeg not found, attempting installation...")
            try:
                self._install_ffmpeg()
            except DependencyError as e:
                raise DependencyError(f"FFmpeg installation failed: {e}")

        # Get metadata
        metadata = get_spotify_metadata(spotify_url)

        # Prepare download
        user_download_dir = self._get_user_download_dir(user_id)
        command = self._prepare_download_command(
            spotify_url, user_download_dir, quality
        )

        # Log download attempt
        log_download_attempt(logger, user_id, spotify_url, quality)

        # Execute download
        try:
            result = self._execute_download(command)

            # Process downloaded files
            files = self._process_downloaded_files(user_download_dir)

            if not files:
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
                metadata=metadata,
                total_size=total_size,
            )

        except (DownloadError, DependencyError) as e:
            log_download_error(logger, user_id, str(e), spotify_url)
            return DownloadResult(success=False, error=str(e), metadata=metadata)


def download_and_send(bot: TeleBot, message: Message, spotify_url: str, quality: int, user_id: int = None):
    """
    Download Spotify track and send to user with enhanced error handling.

    Args:
        bot: Telegram bot instance
        message: User message
        spotify_url: Spotify URL to download
        quality: Audio quality
        user_id: Telegram user ID (if None, uses message.chat.id for backwards compatibility)
    """
    if user_id is None:
        user_id = message.chat.id
    messages = get_messages(user_id)

    # Initialize downloader
    downloader = SpotifyDownloader()

    try:
        # Check dependencies first
        deps = downloader.check_dependencies()

        if not deps["spotdl"]:
            bot.send_message(user_id, messages.get("spotdl_not_installed"))
            return

        if not deps["ffmpeg"]:
            bot.send_message(user_id, messages.get("ffmpeg_installing"))
            try:
                downloader._install_ffmpeg()
                bot.send_message(user_id, messages.get("ffmpeg_installed"))
            except DependencyError as e:
                template = messages.get(
                    "ffmpeg_install_failed",
                    "❌ Failed to install FFmpeg: {}",
                )
                bot.send_message(user_id, template.format(str(e)))
                return

        # Start download
        result = downloader.download(spotify_url, user_id, quality)

        if not result.success:
            # Send appropriate error message
            error_text = (result.error or "").lower()

            if "rate limit" in error_text:
                bot.send_message(user_id, messages.get("retry_failed"))
            elif "audio provider error" in error_text or "yt-dlp" in error_text:
                bot.send_message(user_id, messages.get("audio_provider_error"))
            elif (
                "invalid spotify track id" in error_text
                or "invalid spotify url" in error_text
            ):
                bot.send_message(user_id, messages.get("invalid_url"))
            elif "not found" in error_text or "unavailable" in error_text:
                bot.send_message(user_id, messages.get("no_files_downloaded"))
            elif "no files were downloaded" in error_text:
                bot.send_message(user_id, messages.get("no_files_downloaded"))
            elif "timed out" in error_text:
                bot.send_message(user_id, messages.get("download_timeout"))
            else:
                bot.send_message(user_id, messages.get("unexpected_error"))
            return

        # Send downloaded files
        files_sent = 0
        for file_path in result.files:
            try:
                filename = os.path.basename(file_path)

                # Prepare caption with metadata
                caption = messages.get("download_complete", filename=filename)
                if result.metadata and result.metadata.get("valid"):
                    metadata = result.metadata
                    if metadata.get("title") and metadata.get("artist"):
                        caption = f"🎵 {metadata['title']}\n👤 {metadata['artist']}"
                        if metadata.get("album"):
                            caption += f"\n💿 {metadata['album']}"

                # Send file
                with open(file_path, "rb") as f:
                    bot.send_audio(user_id, f, caption=caption)
                    files_sent += 1

                # Clean up file after sending
                os.remove(file_path)

            except Exception as e:
                logger.error("Failed to send file %s: %s", file_path, e)
                bot.send_message(user_id, messages.get("file_send_error", error=str(e)))

        if files_sent == 0:
            bot.send_message(user_id, messages.get("no_files_downloaded"))

        # Clean up empty directory
        try:
            user_dir = downloader._get_user_download_dir(user_id)
            if not os.listdir(user_dir):
                os.rmdir(user_dir)
        except Exception:
            pass  # Ignore cleanup errors

    except Exception as e:
        logger.error("Unexpected error in download_and_send: %s", e)
        bot.send_message(user_id, messages.get("unexpected_error"))