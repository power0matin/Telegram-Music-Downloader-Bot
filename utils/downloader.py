import os
import subprocess
import time
from telebot import TeleBot

def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def install_ffmpeg():
    # نمونه برای Ubuntu/Debian
    subprocess.run("apt-get update && apt-get install -y ffmpeg", shell=True)

def download_and_send(bot: TeleBot, message, spotify_link: str, quality: str):
    if not is_ffmpeg_installed():
        bot.send_message(message.chat.id, "FFmpeg not found. Installing FFmpeg...")
        install_ffmpeg()
        bot.send_message(message.chat.id, "FFmpeg installed successfully.")

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    bitrate = "128k" if quality == "128" else "320k"
    command = f"spotdl download {spotify_link} --bitrate {bitrate} --output {output_dir}/"

    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            break
        else:
            error_output = result.stderr.lower()
            if "rate limit" in error_output or "retry" in error_output:
                bot.send_message(message.chat.id, f"Rate limit hit. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                bot.send_message(message.chat.id, f"Download error: {result.stderr}")
                return

    # ارسال فایل‌ها
    sent_any = False
    for filename in os.listdir(output_dir):
        if filename.endswith(".mp3"):
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "rb") as f:
                bot.send_audio(message.chat.id, f)
                sent_any = True
            os.remove(file_path)

    if not sent_any:
        bot.send_message(message.chat.id, "No audio file was downloaded.")

    # اگر فولدر خالی بود حذفش کن
    if not os.listdir(output_dir):
        os.rmdir(output_dir)
