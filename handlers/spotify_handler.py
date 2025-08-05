from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue_functions import add_to_queue
from .callback_handler import register_callback_handler

def is_spotify_url(url):
    """Check if the URL is a valid Spotify URL."""
    spotify_patterns = [
        "open.spotify.com/track/",
        "open.spotify.com/album/",
        "open.spotify.com/playlist/",
        "spotify.com/track/",
        "spotify.com/album/", 
        "spotify.com/playlist/"
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
            bot.reply_to(message, "🎵 Welcome to Spotify Downloader Bot!\n\nPlease send a valid Spotify link:\n• Track: https://open.spotify.com/track/...\n• Album: https://open.spotify.com/album/...\n• Playlist: https://open.spotify.com/playlist/...")
            return

        if not is_spotify_url(text):
            bot.reply_to(message, "❌ This doesn't appear to be a valid Spotify link.\n\nPlease send a valid Spotify link for:\n• Track\n• Album\n• Playlist")
            return

        link = text
        add_to_queue(link, message.chat.id)

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🎵 128 kbps", callback_data=f"quality|128|{link}"),
            InlineKeyboardButton("🎶 320 kbps (HQ)", callback_data=f"quality|320|{link}")
        )
        bot.reply_to(message, "✅ Valid Spotify link detected!\nPlease select your desired quality:", reply_markup=markup)
    
    # Also register the callback handler
    register_callback_handler(bot)