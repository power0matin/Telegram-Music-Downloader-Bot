import telebot
import subprocess
import os
import requests
from io import BytesIO

# Add your Telegram bot token here
BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Please send the Spotify link for the song, album, or playlist you want to download.")


@bot.message_handler(func=lambda message: True)
def handle_spotify_link(message):
    spotify_link = message.text

    # Send quality selection buttons
    # Limit the length of callback_data to prevent errors
    data_128 = f'128|{spotify_link}'[:64]
    data_320 = f'320|{spotify_link}'[:64]

    # Create quality selection buttons
    markup = telebot.types.InlineKeyboardMarkup()
    btn_128 = telebot.types.InlineKeyboardButton('128 kbps', callback_data=data_128)
    btn_320 = telebot.types.InlineKeyboardButton('320 kbps', callback_data=data_320)
    markup.add(btn_128, btn_320)

    # Send a message with the buttons
    bot.reply_to(message, "Please select your desired quality:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    quality, spotify_link = call.data.split('|')
    download_and_send(call.message, spotify_link, quality)


def download_and_send(message, spotify_link, quality):
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    if quality == '128':
        bitrate = '128k'
    elif quality == '320':
        bitrate = '320k'
    else:
        bot.reply_to(message, "Invalid quality!")
        return

    # Run the spotdl command to download
    command = f"spotdl download {spotify_link} --bitrate {bitrate} --output {output_dir}/"
    subprocess.run(command, shell=True)

    # Send the downloaded files and delete them afterwards
    for filename in os.listdir(output_dir):
        if filename.endswith(".mp3"):
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'rb') as f:
                bot.send_audio(message.chat.id, f)
            os.remove(file_path)

    # Remove the downloads folder after sending the files
    os.rmdir(output_dir)


bot.polling()
