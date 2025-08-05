import os
import subprocess
import time
from telebot import TeleBot
from .variables import DOWNLOAD_DIR

def is_ffmpeg_installed():
    """Check if FFmpeg is installed on the system."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def is_spotdl_installed():
    """Check if spotdl is installed."""
    try:
        subprocess.run(["spotdl", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_ffmpeg():
    """Install FFmpeg using system package manager."""
    try:
        # Try different package managers
        if os.path.exists("/usr/bin/apt-get"):
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)
        elif os.path.exists("/usr/bin/yum"):
            subprocess.run(["yum", "install", "-y", "ffmpeg"], check=True)
        elif os.path.exists("/usr/bin/pacman"):
            subprocess.run(["pacman", "-S", "--noconfirm", "ffmpeg"], check=True)
        else:
            raise Exception("Unsupported package manager")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to install FFmpeg: {e}")

def validate_spotify_url(url):
    """Validate if the URL is a valid Spotify URL."""
    spotify_domains = ["open.spotify.com", "spotify.com"]
    return any(domain in url for domain in spotify_domains)

def download_and_send(bot: TeleBot, message, spotify_link: str, quality: str):
    """Download Spotify track and send to user."""
    
    # Validate input
    if not validate_spotify_url(spotify_link):
        bot.send_message(message.chat.id, "❌ Invalid Spotify URL. Please provide a valid Spotify link.")
        return
    
    # Check required tools
    if not is_spotdl_installed():
        bot.send_message(message.chat.id, "❌ spotdl is not installed. Please install it using: pip install spotdl")
        return
    
    if not is_ffmpeg_installed():
        bot.send_message(message.chat.id, "🔧 FFmpeg not found. Installing FFmpeg...")
        try:
            install_ffmpeg()
            bot.send_message(message.chat.id, "✅ FFmpeg installed successfully.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed to install FFmpeg: {e}")
            return

    # Create user-specific download directory
    user_download_dir = os.path.join(DOWNLOAD_DIR, str(message.chat.id))
    os.makedirs(user_download_dir, exist_ok=True)

    # Validate quality
    if quality not in ["128", "320"]:
        quality = "320"  # Default fallback
    
    bitrate = f"{quality}k"
    
    # Prepare download command
    command = [
        "spotdl", "download", spotify_link,
        "--bitrate", bitrate,
        "--output", user_download_dir,
        "--format", "mp3"
    ]

    max_retries = 5
    retry_delay = 5  # seconds

    # Download with retry logic
    for attempt in range(max_retries):
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            if result.returncode == 0:
                break
            else:
                error_output = result.stderr.lower()
                if "rate limit" in error_output or "retry" in error_output:
                    if attempt < max_retries - 1:
                        bot.send_message(message.chat.id, f"⏳ Rate limit hit. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        bot.send_message(message.chat.id, "❌ Download failed after multiple retries due to rate limiting.")
                        return
                else:
                    bot.send_message(message.chat.id, f"❌ Download error: {result.stderr}")
                    return
        except subprocess.TimeoutExpired:
            bot.send_message(message.chat.id, "❌ Download timed out. Please try again later.")
            return
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Unexpected error: {e}")
            return

    # Send downloaded files
    sent_any = False
    try:
        for filename in os.listdir(user_download_dir):
            if filename.endswith(".mp3"):
                file_path = os.path.join(user_download_dir, filename)
                try:
                    with open(file_path, "rb") as f:
                        bot.send_audio(message.chat.id, f, caption=f"🎵 Downloaded: {filename}")
                        sent_any = True
                    os.remove(file_path)  # Clean up after sending
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ Failed to send file {filename}: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error accessing download directory: {e}")
        return

    if not sent_any:
        bot.send_message(message.chat.id, "❌ No audio file was downloaded. Please check the Spotify link and try again.")

    # Clean up empty directory
    try:
        if not os.listdir(user_download_dir):
            os.rmdir(user_download_dir)
    except Exception:
        pass  # Ignore cleanup errors
