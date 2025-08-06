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
    files: List[str] = None
    error: str = None
    metadata: Dict[str, Any] = None
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

        logger.debug(f"Dependency check: {dependencies}")
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
        Attempt to install FFmpeg (Linux only).

        Returns:
            True if installation successful

        Raises:
            DependencyError: If installation fails
        """
        try:
            logger.info("Attempting to install FFmpeg...")

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
            else:
                raise DependencyError("FFmpeg installation verification failed")

        except subprocess.CalledProcessError as e:
            raise DependencyError(f"Failed to install FFmpeg: {e}")
        except subprocess.TimeoutExpired:
            raise DependencyError("FFmpeg installation timed out")

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
            output_dir: Output directory
            quality: Audio quality (128 or 320)

        Returns:
            List of command arguments
        """
        # Validate and sanitize quality
        if quality not in [128, 320]:
            quality = config.default_quality

        bitrate = f"{quality}k"

        # Build command
        command = [
            "spotdl",
            "download",
            spotify_url,
            "--bitrate",
            bitrate,
            "--output",
            output_dir,
            "--format",
            "mp3",
            "--overwrite",
            "skip",  # Skip if file already exists
        ]

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
                logger.debug(f"Download attempt {attempt + 1}/{max_retries}")

                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=timeout
                )

                if result.returncode == 0:
                    return result

                # Check for specific error types
                error_output = result.stderr.lower()

                if "rate limit" in error_output or "retry" in error_output:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit, retrying in {retry_delay}s")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise DownloadError(
                            "Rate limit exceeded after multiple retries"
                        )

                elif "not found" in error_output or "unavailable" in error_output:
                    raise DownloadError("Track not found or unavailable")

                elif "network" in error_output or "connection" in error_output:
                    raise DownloadError("Network connection error")

                else:
                    raise DownloadError(f"Download failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    logger.warning(f"Download timed out, retrying...")
                    continue
                else:
                    raise DownloadError("Download timed out after multiple attempts")

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Download error: {e}, retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
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
        files = []

        try:
            for filename in os.listdir(download_dir):
                if filename.endswith(".mp3"):
                    file_path = os.path.join(download_dir, filename)
                    file_stat = os.stat(file_path)

                    # Check file size
                    if file_stat.st_size > self.max_file_size:
                        logger.warning(f"File {filename} exceeds size limit")
                        continue

                    file_info = {
                        "filename": filename,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "size_mb": file_stat.st_size / (1024 * 1024),
                    }

                    files.append(file_info)
                    logger.debug(
                        f"Processed file: {filename} ({file_info['size_mb']:.2f}MB)"
                    )

        except Exception as e:
            logger.error(f"Error processing downloaded files: {e}")
            raise DownloadError(f"Error processing downloaded files: {e}")

        return files

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


def download_and_send(bot: TeleBot, message: Message, spotify_url: str, quality: int):
    """
    Download Spotify track and send to user with enhanced error handling.

    Args:
        bot: Telegram bot instance
        message: User message
        spotify_url: Spotify URL to download
        quality: Audio quality
    """
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
                bot.send_message(
                    user_id, messages.get("ffmpeg_install_failed", error=str(e))
                )
                return

        # Start download
        result = downloader.download(spotify_url, user_id, quality)

        if not result.success:
            # Send appropriate error message
            if "Rate limit" in result.error:
                bot.send_message(user_id, messages.get("retry_failed"))
            elif "not found" in result.error or "unavailable" in result.error:
                bot.send_message(user_id, messages.get("no_files_downloaded"))
            elif "timed out" in result.error:
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
                logger.error(f"Failed to send file {file_path}: {e}")
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
        logger.error(f"Unexpected error in download_and_send: {e}")
        bot.send_message(user_id, messages.get("unexpected_error"))
