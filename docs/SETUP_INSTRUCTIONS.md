# Spotify Downloader Bot - Setup Instructions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (will be installed automatically if missing)
- Telegram Bot Token

### 1. Clone and Setup Environment

```bash
# Navigate to the project directory
cd /path/to/your/project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Telegram Bot Token

1. Start a chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy your bot token (it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure the Bot

Set your bot token as an environment variable:

```bash
export BOT_TOKEN="your_bot_token_here"
```

Or create a `.env` file in the project root:

```
BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

#### Option 1: Using the startup script (recommended)

```bash
./start_bot.sh
```

#### Option 2: Manual start

```bash
source venv/bin/activate
python3 bot.py
```

## 🎯 Features

- ✅ Download Spotify tracks, albums, and playlists
- ✅ Choose between 128 kbps and 320 kbps quality
- ✅ Automatic FFmpeg installation
- ✅ User-friendly error messages
- ✅ Rate limiting protection with retry logic
- ✅ Clean file management

## 🔧 Troubleshooting

### Common Issues

1. **"No module named 'telebot'"**

   - Make sure virtual environment is activated
   - Run: `pip install -r requirements.txt`

2. **"FFmpeg not found"**

   - The bot will try to install FFmpeg automatically
   - Manual installation: `sudo apt install ffmpeg` (Ubuntu/Debian)

3. **"BOT_TOKEN not set"**

   - Set the environment variable: `export BOT_TOKEN="your_token"`
   - Or add it to a `.env` file

4. **Download failures**
   - Check if the Spotify URL is valid
   - Ensure internet connection is stable
   - Some content may be geo-restricted

### Logs and Debugging

The bot provides detailed error messages. If you encounter issues:

1. Check the console output for error messages
2. Verify your bot token is correct
3. Ensure Spotify URLs are properly formatted
4. Check internet connectivity

## 📝 Usage

1. Start a chat with your bot
2. Send any Spotify link (track, album, or playlist)
3. Choose your preferred quality (128kbps or 320kbps)
4. Wait for the download and receive your audio files!

## 🔒 Security Note

- Never share your bot token publicly
- Use environment variables or secure configuration files
- Consider using a `.env` file for local development

## 📁 Project Structure

```
├── bot.py                 # Main bot entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── start_bot.sh         # Startup script
├── handlers/            # Bot message handlers
│   ├── __init__.py
│   ├── spotify_handler.py
│   └── callback_handler.py
├── utils/               # Utility modules
│   ├── __init__.py
│   ├── downloader.py    # Download functionality
│   ├── queue_functions.py
│   └── variables.py
├── queue/               # Queue storage (auto-created)
└── downloads/           # Temporary download directory (auto-created)
```
