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
                "🎵 Welcome to the Spotify Link Preview Bot!\n\n"
                "Send a Spotify link to see the metadata preview and open it "
                "in Spotify. Audio delivery is disabled by default.\n"
                "• Track: https://open.spotify.com/track/...\n"
                "• Album: https://open.spotify.com/album/...\n"
                "• Playlist: https://open.spotify.com/playlist/...\n\n"
                "Use /help for more information."
            ),
            "help": (
                "🎵 **Spotify Link Preview Bot Help**\n\n"
                "**Available Commands:**\n"
                "/start - Show welcome message\n"
                "/help - Show this help message\n\n"
                "**How to use:**\n"
                "1. Send a public Spotify track, album, or playlist link\n"
                "2. Review the limited metadata preview\n"
                "3. Open the item directly in Spotify\n\n"
                "Audio-file delivery is disabled by default. It may only be "
                "enabled by an operator after obtaining required written platform "
                "permissions and all rights-holder licences. See docs/COMPLIANCE.md.\n\n"
                "**Rate limits:**\n"
                f"• {config.rate_limit_requests} requests per {config.rate_limit_window_seconds} seconds"
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
            "worker_start_failed_retry": (
                "⚠️ The download worker could not start. Your request is still available; "
                "tap a quality button below to retry."
            ),
            "server_busy": (
                "⏳ All download slots are busy. Please tap the quality button again "
                "in a moment."
            ),
            "invalid_spotify_link": "❌ Invalid Spotify link.",
            "rate_limit_exceeded": (
                "⏳ You're sending requests too quickly. "
                "Please try again in {seconds} seconds."
            ),
            "download_timeout": "❌ Download timed out. Please try again later.",
            "unexpected_error": "❌ An unexpected error occurred during download.",
            "no_files_downloaded": (
                "❌ No audio file was downloaded. "
                "Please check the Spotify link and try again."
            ),
            "file_send_error": (
                "❌ The audio was downloaded, but Telegram could not receive the file. "
                "Please try again."
            ),
            "file_too_large": (
                "❌ The downloaded audio exceeds this bot's safe Telegram upload limit "
                "of {limit} MB."
            ),
            "directory_error": "❌ Error accessing download directory.",
            "spotdl_not_installed": (
                "❌ spotdl is not installed. " "Please contact the administrator."
            ),
            "ffmpeg_not_installed": (
                "❌ FFmpeg is not installed on the server. "
                "Please contact the administrator."
            ),
            "spotdl_incompatible": (
                "❌ The server has an incompatible spotDL version. "
                "Please contact the administrator."
            ),
            "audio_source_unavailable": (
                "⚠️ None of the configured audio sources could provide this item. "
                "Please try again later or contact the administrator."
            ),
            "youtube_signin_required": (
                "⚠️ YouTube rejected the server request. "
                "The administrator may need to configure YouTube cookies or a proxy."
            ),
            "track_not_found": "❌ Track not found. Please check the Spotify link.",
            "track_unavailable": "❌ This track is currently unavailable.",
            # Success messages
            "metadata_only": (
                "ℹ️ Audio delivery is disabled. Here is the available Spotify metadata preview:"
            ),
            "audio_delivery_disabled": "Audio-file delivery is disabled on this bot.",
            "open_on_spotify": "Open on Spotify",
            "link_detected": (
                "✅ Valid Spotify link detected!\n"
                "Please choose your preferred quality:"
            ),
            "quality_selected": (
                "🎵 {quality} kbps quality selected. Download starting..."
            ),
            "downloading": "🎵 Downloading at {quality} kbps...\nPlease wait.",
            "download_complete": "🎵 Downloaded: {filename}",
            "partial_download": (
                "⚠️ Partial result: {sent} file(s) sent; {failed} Telegram upload(s) failed; "
                "{source_failed} source item(s) failed; {skipped} local audio file(s) skipped."
            ),
            "retry_attempt": (
                "⏳ Rate limit hit. Retrying in {} seconds... " "(Attempt {}/{})"
            ),
            "retry_failed": (
                "❌ Download failed after multiple retries due to rate limiting."
            ),
            # Button labels
            "quality_128": "🎵 128 kbps",
            "quality_320": "🎶 320 kbps",
        },
        "fa": {
            # Welcome and help messages
            "welcome": (
                "🎵 به ربات پیش‌نمایش لینک Spotify خوش آمدید!\n\n"
                "یک لینک Spotify بفرستید تا اطلاعات محدود آن نمایش داده شود "
                "و بتوانید مورد را مستقیماً در Spotify باز کنید. ارسال فایل صوتی "
                "به‌صورت پیش‌فرض غیرفعال است.\n"
                "• آهنگ: https://open.spotify.com/track/...\n"
                "• آلبوم: https://open.spotify.com/album/...\n"
                "• پلی‌لیست: https://open.spotify.com/playlist/...\n\n"
                "برای اطلاعات بیشتر از /help استفاده کنید."
            ),
            "help": (
                "🎵 **راهنمای ربات پیش‌نمایش لینک Spotify**\n\n"
                "**دستورات موجود:**\n"
                "/start - نمایش پیام خوش‌آمدگویی\n"
                "/help - نمایش این راهنما\n\n"
                "**نحوه استفاده:**\n"
                "۱. لینک عمومی آهنگ، آلبوم یا پلی‌لیست Spotify را بفرستید\n"
                "۲. پیش‌نمایش محدود اطلاعات را ببینید\n"
                "۳. مورد را مستقیماً در Spotify باز کنید\n\n"
                "ارسال فایل صوتی به‌صورت پیش‌فرض غیرفعال است. فعال‌سازی آن فقط "
                "پس از دریافت مجوزهای کتبی لازم از پلتفرم‌ها و مجوزهای صاحبان "
                "حقوق فایل امکان‌پذیر است. جزئیات در docs/COMPLIANCE.md.\n\n"
                "**محدودیت نرخ:**\n"
                f"• {config.rate_limit_requests} درخواست در هر {config.rate_limit_window_seconds} ثانیه"
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
            "worker_start_failed_retry": (
                "⚠️ شروع پردازش دانلود ناموفق بود، اما درخواست شما هنوز معتبر است؛ "
                "برای تلاش دوباره یکی از دکمه‌های کیفیت زیر را بزنید."
            ),
            "server_busy": (
                "⏳ ظرفیت دانلود ربات فعلاً پر است. کمی بعد دوباره همان دکمه کیفیت "
                "را بزنید."
            ),
            "invalid_spotify_link": "❌ لینک معتبر Spotify نیست.",
            "rate_limit_exceeded": (
                "⏳ شما خیلی سریع درخواست ارسال می‌کنید. "
                "لطفاً {seconds} ثانیه دیگر دوباره تلاش کنید."
            ),
            "download_timeout": "❌ دانلود متوقف شد. لطفاً بعداً تلاش کنید.",
            "unexpected_error": "❌ خطای غیرمنتظره در حین دانلود رخ داد.",
            "no_files_downloaded": (
                "❌ هیچ فایل صوتی دانلود نشد. "
                "لطفاً لینک Spotify را بررسی کرده و دوباره تلاش کنید."
            ),
            "file_send_error": (
                "❌ فایل دانلود شد، اما ارسال آن به تلگرام ناموفق بود. "
                "لطفاً دوباره تلاش کنید."
            ),
            "file_too_large": (
                "❌ حجم فایل صوتی از سقف امن {limit} مگابایتی ارسال تلگرام برای این ربات بیشتر است."
            ),
            "directory_error": "❌ خطا در دسترسی به پوشه دانلود.",
            "spotdl_not_installed": (
                "❌ spotdl نصب نشده است. " "لطفاً با مدیر تماس بگیرید."
            ),
            "ffmpeg_not_installed": (
                "❌ FFmpeg روی سرور نصب نیست. لطفاً با مدیر تماس بگیرید."
            ),
            "spotdl_incompatible": (
                "❌ نسخه spotDL روی سرور با ربات سازگار نیست. "
                "لطفاً با مدیر تماس بگیرید."
            ),
            "audio_source_unavailable": (
                "⚠️ هیچ‌کدام از منابع صوتی تنظیم‌شده نتوانستند این مورد را دریافت کنند. "
                "لطفاً بعداً دوباره تلاش کنید."
            ),
            "youtube_signin_required": (
                "⚠️ یوتیوب درخواست سرور را رد کرد. "
                "ممکن است مدیر نیاز به تنظیم کوکی یا پروکسی داشته باشد."
            ),
            "track_not_found": "❌ آهنگ پیدا نشد. لطفاً لینک Spotify را بررسی کنید.",
            "track_unavailable": "❌ این آهنگ در حال حاضر در دسترس نیست.",
            # Success messages
            "metadata_only": (
                "ℹ️ ارسال فایل صوتی غیرفعال است. پیش‌نمایش اطلاعات در دسترس Spotify:"
            ),
            "audio_delivery_disabled": "ارسال فایل صوتی در این ربات غیرفعال است.",
            "open_on_spotify": "باز کردن در Spotify",
            "link_detected": (
                "✅ لینک معتبر Spotify شناسایی شد!\n"
                "لطفاً کیفیت مورد نظر خود را انتخاب کنید:"
            ),
            "quality_selected": (
                "🎵 کیفیت {quality} کیلوبیت بر ثانیه انتخاب شد. دانلود شروع می‌شود..."
            ),
            "downloading": (
                "🎵 در حال دانلود با کیفیت {quality} kbps...\nلطفاً صبر کنید."
            ),
            "download_complete": "🎵 دانلود شد: {filename}",
            "partial_download": (
                "⚠️ نتیجه ناقص بود: {sent} فایل ارسال شد؛ {failed} ارسال تلگرامی ناموفق بود؛ "
                "{source_failed} مورد از منبع صوتی دریافت نشد؛ {skipped} فایل صوتی محلی "
                "قابل پردازش یا ارسال نبود و کنار گذاشته شد."
            ),
            "retry_attempt": (
                "⏳ به حد مجاز رسیده. تلاش مجدد در {} ثانیه... " "(تلاش {}/{})"
            ),
            "retry_failed": (
                "❌ دانلود پس از چندین تلاش به دلیل محدودیت نرخ ناموفق بود."
            ),
            # Button labels
            "quality_128": "🎵 ۱۲۸ کیلوبیت",
            "quality_320": "🎶 ۳۲۰ کیلوبیت",
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
