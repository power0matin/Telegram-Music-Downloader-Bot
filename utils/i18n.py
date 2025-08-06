"""
Internationalization (i18n) support for Spotify Bot.

This module provides multilingual support for bot messages.
"""

from typing import Dict, Any
from config import config


class Messages:
    """Message translations for different languages."""

    TRANSLATIONS = {
        "en": {
            # Welcome and help messages
            "welcome": (
                "🎵 Welcome to the Spotify Downloader Bot!\n\n"
                "Send me a valid Spotify link and I'll download it for you:\n"
                "• Track: https://open.spotify.com/track/...\n"
                "• Album: https://open.spotify.com/album/...\n"
                "• Playlist: https://open.spotify.com/playlist/...\n\n"
                "Use /help for more information."
            ),
            "help": (
                "🎵 **Spotify Downloader Bot Help**\n\n"
                "**Available Commands:**\n"
                "/start - Show welcome message\n"
                "/help - Show this help message\n\n"
                "**How to use:**\n"
                "1. Send me a Spotify link\n"
                "2. Choose audio quality (128kbps or 320kbps)\n"
                "3. Wait for download to complete\n"
                "4. Enjoy your music!\n\n"
                "**Supported formats:**\n"
                "• Tracks\n"
                "• Albums\n"
                "• Playlists\n\n"
                "**Quality options:**\n"
                "• 128 kbps - Good quality, smaller file size\n"
                "• 320 kbps - High quality, larger file size\n\n"
                "**Rate limits:**\n"
                f"• {config.rate_limit_requests} downloads per {config.rate_limit_window_seconds} seconds\n\n"
                "**Note:** This bot downloads music from YouTube based on Spotify metadata."
            ),
            # Error messages
            "text_only": "Please send a text message containing a Spotify link.",
            "invalid_url": (
                "❌ This doesn't appear to be a valid Spotify link.\n\n"
                "Please send a valid link for:\n"
                "• Track\n• Album\n• Playlist"
            ),
            "invalid_callback": "❌ Invalid callback data.",
            "link_not_found": "❌ Link not found or expired.",
            "invalid_spotify_link": "❌ Invalid Spotify link.",
            "rate_limit_exceeded": (
                "⏳ You're sending requests too quickly. "
                f"Please wait {config.rate_limit_window_seconds} seconds between downloads."
            ),
            "download_timeout": "❌ Download timed out. Please try again later.",
            "unexpected_error": "❌ An unexpected error occurred during download.",
            "no_files_downloaded": (
                "❌ No audio file was downloaded. "
                "Please check the Spotify link and try again."
            ),
            "file_send_error": "❌ Failed to send file: {}",
            "directory_error": "❌ Error accessing download directory.",
            "spotdl_not_installed": (
                "❌ spotdl is not installed. " "Please contact the administrator."
            ),
            "ffmpeg_installing": "🔧 FFmpeg not found. Installing FFmpeg...",
            "ffmpeg_installed": "✅ FFmpeg installed successfully.",
            "ffmpeg_install_failed": "❌ Failed to install FFmpeg: {}",
            # Success messages
            "link_detected": (
                "✅ Valid Spotify link detected!\n"
                "Please choose your preferred quality:"
            ),
            "quality_selected": ("🎵 {} kbps quality selected. Download starting..."),
            "downloading": "🎵 Downloading at {} kbps...\nPlease wait.",
            "download_complete": "🎵 Downloaded: {}",
            "retry_attempt": (
                "⏳ Rate limit hit. Retrying in {} seconds... " "(Attempt {}/{})"
            ),
            "retry_failed": (
                "❌ Download failed after multiple retries due to rate limiting."
            ),
            # Button labels
            "quality_128": "🎵 128 kbps",
            "quality_320": "🎶 320 kbps (HQ)",
        },
        "fa": {
            # Welcome and help messages
            "welcome": (
                "🎵 به ربات دانلود Spotify خوش آمدید!\n\n"
                "لطفاً یک لینک معتبر Spotify ارسال کنید:\n"
                "• آهنگ: https://open.spotify.com/track/...\n"
                "• آلبوم: https://open.spotify.com/album/...\n"
                "• پلی‌لیست: https://open.spotify.com/playlist/...\n\n"
                "برای اطلاعات بیشتر از /help استفاده کنید."
            ),
            "help": (
                "🎵 **راهنمای ربات دانلود Spotify**\n\n"
                "**دستورات موجود:**\n"
                "/start - نمایش پیام خوش‌آمدگویی\n"
                "/help - نمایش این راهنما\n\n"
                "**نحوه استفاده:**\n"
                "۱. یک لینک Spotify ارسال کنید\n"
                "۲. کیفیت صوتی مورد نظر را انتخاب کنید\n"
                "۳. منتظر اتمام دانلود بمانید\n"
                "۴. از موسیقی خود لذت ببرید!\n\n"
                "**فرمت‌های پشتیبانی شده:**\n"
                "• آهنگ‌ها\n"
                "• آلبوم‌ها\n"
                "• پلی‌لیست‌ها\n\n"
                "**گزینه‌های کیفیت:**\n"
                "• ۱۲۸ کیلوبیت - کیفیت خوب، حجم کمتر\n"
                "• ۳۲۰ کیلوبیت - کیفیت بالا، حجم بیشتر\n\n"
                "**محدودیت‌های نرخ:**\n"
                f"• {config.rate_limit_requests} دانلود در هر {config.rate_limit_window_seconds} ثانیه\n\n"
                "**توجه:** این ربات موسیقی را از یوتیوب بر اساس اطلاعات Spotify دانلود می‌کند."
            ),
            # Error messages
            "text_only": "لطفاً یک پیام متنی حاوی لینک Spotify ارسال کنید.",
            "invalid_url": (
                "❌ این لینک به نظر یک لینک معتبر Spotify نیست.\n\n"
                "لطفاً یک لینک معتبر برای:\n"
                "• آهنگ\n• آلبوم\n• پلی‌لیست ارسال کنید."
            ),
            "invalid_callback": "❌ داده callback نامعتبر است.",
            "link_not_found": "❌ لینک یافت نشد یا منقضی شده است.",
            "invalid_spotify_link": "❌ لینک معتبر Spotify نیست.",
            "rate_limit_exceeded": (
                "⏳ شما خیلی سریع درخواست ارسال می‌کنید. "
                f"لطفاً {config.rate_limit_window_seconds} ثانیه بین دانلودها صبر کنید."
            ),
            "download_timeout": "❌ دانلود متوقف شد. لطفاً بعداً تلاش کنید.",
            "unexpected_error": "❌ خطای غیرمنتظره در حین دانلود رخ داد.",
            "no_files_downloaded": (
                "❌ هیچ فایل صوتی دانلود نشد. "
                "لطفاً لینک Spotify را بررسی کرده و دوباره تلاش کنید."
            ),
            "file_send_error": "❌ ارسال فایل ناموفق بود: {}",
            "directory_error": "❌ خطا در دسترسی به پوشه دانلود.",
            "spotdl_not_installed": (
                "❌ spotdl نصب نشده است. " "لطفاً با مدیر تماس بگیرید."
            ),
            "ffmpeg_installing": "🔧 FFmpeg یافت نشد. در حال نصب FFmpeg...",
            "ffmpeg_installed": "✅ FFmpeg با موفقیت نصب شد.",
            "ffmpeg_install_failed": "❌ نصب FFmpeg ناموفق بود: {}",
            # Success messages
            "link_detected": (
                "✅ لینک معتبر Spotify شناسایی شد!\n"
                "لطفاً کیفیت مورد نظر خود را انتخاب کنید:"
            ),
            "quality_selected": (
                "🎵 کیفیت {} کیلوبیت بر ثانیه انتخاب شد. دانلود شروع می‌شود..."
            ),
            "downloading": "🎵 در حال دانلود با کیفیت {} kbps...\nلطفاً صبر کنید.",
            "download_complete": "🎵 دانلود شد: {}",
            "retry_attempt": (
                "⏳ به حد مجاز رسیده. تلاش مجدد در {} ثانیه... " "(تلاش {}/{})"
            ),
            "retry_failed": (
                "❌ دانلود پس از چندین تلاش به دلیل محدودیت نرخ ناموفق بود."
            ),
            # Button labels
            "quality_128": "🎵 ۱۲۸ کیلوبیت",
            "quality_320": "🎶 ۳۲۰ کیلوبیت (HQ)",
        },
    }

    def __init__(self, language: str = None):
        """
        Initialize messages with specified language.

        Args:
            language: Language code (en, fa). If None, uses config default.
        """
        self.language = language or config.default_language
        if self.language not in self.TRANSLATIONS:
            self.language = config.default_language

    def get(self, key: str, **kwargs) -> str:
        """
        Get translated message.

        Args:
            key: Message key
            **kwargs: Format arguments

        Returns:
            Translated and formatted message
        """
        message = self.TRANSLATIONS[self.language].get(
            key,
            self.TRANSLATIONS[config.default_language].get(
                key, f"Missing translation: {key}"
            ),
        )

        if kwargs:
            try:
                return message.format(**kwargs)
            except (KeyError, ValueError):
                return message

        return message

    def set_language(self, language: str):
        """
        Set the current language.

        Args:
            language: Language code
        """
        if language in self.TRANSLATIONS:
            self.language = language


def get_user_language(user_id: int) -> str:
    """
    Get user's preferred language.

    Args:
        user_id: Telegram user ID

    Returns:
        Language code

    Note: This is a placeholder. In a real implementation,
    you might store user preferences in a database.
    """
    # For now, return default language
    # In the future, this could check a database for user preferences
    return config.default_language


def get_messages(user_id: int = None, language: str = None) -> Messages:
    """
    Get Messages instance for user.

    Args:
        user_id: Telegram user ID
        language: Override language

    Returns:
        Messages instance
    """
    if language:
        return Messages(language)

    if user_id:
        user_lang = get_user_language(user_id)
        return Messages(user_lang)

    return Messages()
