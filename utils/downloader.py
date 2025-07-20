import os
import subprocess
from telebot import TeleBot


def download_and_send(bot: TeleBot, message, spotify_link: str, quality: str):
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    bitrate = "128k" if quality == "128" else "320k"

    command = (
        f"spotdl download {spotify_link} --bitrate {bitrate} --output {output_dir}/"
    )
    subprocess.run(command, shell=True)

    for filename in os.listdir(output_dir):
        if filename.endswith(".mp3"):
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "rb") as f:
                bot.send_audio(message.chat.id, f)
            os.remove(file_path)

    os.rmdir(output_dir)
