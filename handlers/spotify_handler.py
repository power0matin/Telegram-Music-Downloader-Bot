import hashlib
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue_functions import add_to_queue

# Simple in-memory storage for link_id -> link mapping
link_store = {}


def get_link_id(link: str) -> str:
    """Generate a short unique ID for the given link."""
    return hashlib.md5(link.encode()).hexdigest()[:10]


def store_link(link_id: str, link: str):
    """Store the link associated with the link_id."""
    link_store[link_id] = link


def retrieve_link(link_id: str) -> str | None:
    """Retrieve the original link by its ID."""
    return link_store.get(link_id)


def is_spotify_url(url: str) -> bool:
    """Check if the URL is a valid Spotify URL."""
    spotify_patterns = [
        "open.spotify.com/track/",
        "open.spotify.com/album/",
        "open.spotify.com/playlist/",
        "spotify.com/track/",
        "spotify.com/album/",
        "spotify.com/playlist/",
    ]
    return any(pattern in url for pattern in spotify_patterns)


def register_message_handler(bot):
    @bot.message_handler(func=lambda message: True)
    def handle_spotify_link(message: Message):
        if not message.text:
            bot.reply_to(message, "لطفاً یک پیام متنی حاوی لینک Spotify ارسال کنید.")
            return

        text = message.text.strip()

        if not text.startswith("http"):
            bot.reply_to(
                message,
                "🎵 به ربات دانلود Spotify خوش آمدید!\n\nلطفاً یک لینک معتبر Spotify ارسال کنید:\n"
                "• آهنگ: https://open.spotify.com/track/...\n"
                "• آلبوم: https://open.spotify.com/album/...\n"
                "• پلی‌لیست: https://open.spotify.com/playlist/...",
            )
            return

        if not is_spotify_url(text):
            bot.reply_to(
                message,
                "❌ این لینک به نظر یک لینک معتبر Spotify نیست.\n\nلطفاً یک لینک معتبر برای:\n"
                "• آهنگ\n• آلبوم\n• پلی‌لیست ارسال کنید.",
            )
            return

        link = text

        # Generate a short ID for callback data
        link_id = get_link_id(link)
        store_link(link_id, link)

        # Add to queue (ensure this doesn't re-validate or process immediately)
        add_to_queue(link, message.chat.id)

        # Create inline keyboard for quality selection
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🎵 128 kbps", callback_data=f"quality|128|{link_id}"),
            InlineKeyboardButton(
                "🎶 320 kbps (HQ)", callback_data=f"quality|320|{link_id}"
            ),
        )

        bot.reply_to(
            message,
            "✅ لینک معتبر Spotify شناسایی شد!\nلطفاً کیفیت مورد نظر خود را انتخاب کنید:",
            reply_markup=markup,
        )

    # Defer import to avoid circular import
    from .callback_handler import register_callback_handler

    register_callback_handler(bot)
