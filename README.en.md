# Telegram Music Downloader Bot

This project is a Telegram bot that allows users to download music directly from Spotify by sending a Spotify link to the bot. It supports downloading songs, albums, and playlists in different quality formats (128 kbps and 320 kbps).

## Features
- Download songs, albums, and playlists from Spotify.
- Choose download quality (128 kbps or 320 kbps).
- Automatically send downloaded music files to users via Telegram.

## Prerequisites
To run this bot, make sure you have the following installed:
1. **Python 3.7+**
2. **SpotDL** - A tool to download music from Spotify.
3. **python-telegram-bot** - A Python library to interact with the Telegram API.

## Installation

1. **Clone the Repository**
   Start by cloning the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Install Dependencies**
   Install the necessary dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   a) **Set Up Telegram Bot Token:**  
      Obtain your Telegram bot token from the [BotFather](https://core.telegram.org/bots#botfather) on Telegram and add it to the `main.py` file:
      ```python
      BOT_TOKEN = 'YOUR_BOT_TOKEN'
      ```

   b) **SpotDL Configuration:**  
      Ensure SpotDL is correctly installed and configured. Follow the [SpotDL documentation](https://spotdl.readthedocs.io/) for any additional setup if needed.

## Usage

1. **Run the Bot**
   Start the bot by running:
   ```bash
   python main.py
   ```

2. **Using the Bot**
   - **Start:** Send `/start` to the bot to receive initial instructions.
   - **Send Link:** Send a Spotify link (song, album, or playlist) to the bot.
   - **Choose Quality:** After sending the link, the bot will prompt you to choose the download quality (128 kbps or 320 kbps).
   - **Receive File:** Once you select the quality, the bot will download and send the MP3 file to you.

## Issues and Contributions

If you encounter any issues or have suggestions, feel free to open an issue in the [Issues section](https://github.com/yourusername/yourrepository/issues). Contributions are welcome! If you'd like to contribute, please submit a pull request following the contribution guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

---

Happy coding! 🎵🤖
