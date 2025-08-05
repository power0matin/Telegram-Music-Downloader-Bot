import hashlib
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue_functions import add_to_queue
from .callback_handler import register_callback_handler

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
    # Register message handler for Spotify links
    @bot.message_handler(func=lambda message: True)
    def handle_spotify_link(message: Message):
        if not message.text:
            bot.reply_to(message, "Please send a text message with a Spotify link.")
            return

        text = message.text.strip()

        if not text.startswith("http"):
            bot.reply_to(
                message,
                "🎵 Welcome to Spotify Downloader Bot!\n\nPlease send a valid Spotify link:\n"
                "• Track: https://open.spotify.com/track/...\n"
                "• Album: https://open.spotify.com/album/...\n"
                "• Playlist: https://open.spotify.com/playlist/...",
            )
            return

        if not is_spotify_url(text):
            bot.reply_to(
                message,
                "❌ This doesn't appear to be a valid Spotify link.\n\nPlease send a valid Spotify link for:\n"
                "• Track\n• Album\n• Playlist",
            )
            return

        link = text

        # Add to your processing queue (implement this as needed)
        add_to_queue(link, message.chat.id)

        # Generate a short ID for callback data
        link_id = get_link_id(link)
        store_link(link_id, link)

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🎵 128 kbps", callback_data=f"quality|128|{link_id}"),
            InlineKeyboardButton(
                "🎶 320 kbps (HQ)", callback_data=f"quality|320|{link_id}"
            ),
        )

        bot.reply_to(
            message,
            "✅ Valid Spotify link detected!\nPlease select your desired quality:",
            reply_markup=markup,
        )

    # Also register the callback handler to handle button presses
    register_callback_handler(bot)


# You may want to expose retrieve_link for your callback handler usage
