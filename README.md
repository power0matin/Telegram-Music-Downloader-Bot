# 🎵 Spotify Downloader Bot

A powerful Telegram bot that downloads Spotify tracks, albums, and playlists with high-quality audio and user-friendly interface.

## ✨ Features

- 🎵 **Download Spotify Content**: Tracks, albums, and playlists
- 🎚️ **Quality Selection**: Choose between 128kbps and 320kbps
- 🤖 **User-Friendly Interface**: Interactive buttons and helpful messages
- 🔄 **Auto-Retry**: Smart retry mechanism for failed downloads
- 🧹 **Clean Management**: Automatic file cleanup and organization
- ⚡ **Fast Setup**: One-command installation and setup
- 🛡️ **Error Handling**: Comprehensive error messages and recovery
- 🌍 **Multi-Platform**: Works on Linux, macOS, and Windows

## 🚀 Quick Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Internet connection

### Option 1: Automatic Setup (Recommended)
```bash
# Clone the repository
git clone <your-repository-url>
cd spotify-downloader-bot

# Run the setup script (will install everything automatically)
chmod +x setup_bot.sh
./setup_bot.sh
```

### Option 2: Manual Setup
```bash
# Clone the repository
git clone <your-repository-url>
cd spotify-downloader-bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export BOT_TOKEN="your_telegram_bot_token_here"

# Start the bot
./start_bot.sh
```

## 🔑 Getting Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a chat and send `/newbot`
3. Follow the instructions to create your bot
4. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Keep this token secure and private!

## 📋 Configuration

### Environment Variables
Set your bot token using one of these methods:

**Method 1: Environment Variable**
```bash
export BOT_TOKEN="your_telegram_bot_token_here"
```

**Method 2: .env File**
Create a `.env` file in the project root:
```env
BOT_TOKEN=your_telegram_bot_token_here
```

## 🎯 Usage

1. **Start the bot** using `./start_bot.sh`
2. **Open Telegram** and find your bot
3. **Send a Spotify link** (track, album, or playlist)
4. **Choose quality** using the interactive buttons
5. **Wait for download** and receive your audio files!

### Supported Spotify URLs
- **Tracks**: `https://open.spotify.com/track/...`
- **Albums**: `https://open.spotify.com/album/...`
- **Playlists**: `https://open.spotify.com/playlist/...`

## 🔧 Troubleshooting

### Common Issues

**🚫 "No module named 'telebot'"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**🚫 "BOT_TOKEN not set"**
```bash
# Set your bot token
export BOT_TOKEN="your_bot_token_here"
# or create a .env file with BOT_TOKEN=your_token
```

**🚫 "FFmpeg not found"**
- The bot will try to install FFmpeg automatically
- Manual installation: `sudo apt install ffmpeg` (Ubuntu/Debian)

**🚫 "Permission denied" for setup_bot.sh**
```bash
chmod +x setup_bot.sh
chmod +x start_bot.sh
```

**🚫 Download failures**
- Verify the Spotify URL is correct and accessible
- Check your internet connection
- Some content may be geo-restricted
- Try again after a few minutes (rate limiting)

### Getting Help
- Check the console output for detailed error messages
- Ensure all dependencies are installed correctly
- Verify your bot token is valid
- Make sure Spotify URLs are properly formatted

## 📁 Project Structure

```
spotify-downloader-bot/
├── 🤖 bot.py                    # Main bot entry point
├── ⚙️ config.py                 # Configuration management  
├── 📦 requirements.txt          # Python dependencies
├── 🚀 start_bot.sh             # Bot startup script
├── 🛠️ setup_bot.sh             # Complete setup script
├── 📖 README.md                # English documentation
├── 📖 README.fa.md             # Persian documentation
├── 📁 handlers/                # Bot message handlers
│   ├── __init__.py
│   ├── spotify_handler.py      # Main message handling
│   └── callback_handler.py     # Button interactions
├── 📁 utils/                   # Utility modules
│   ├── __init__.py
│   ├── downloader.py           # Download functionality
│   ├── queue_functions.py      # Queue management
│   └── variables.py            # Path configurations
├── 📁 queue/                   # Download queue storage
└── 📁 downloads/               # Temporary download directory
```

## 🔒 Security & Privacy

- **Never share your bot token** publicly
- Use environment variables or `.env` files for configuration
- The bot automatically cleans up downloaded files after sending
- User-specific download directories prevent file conflicts
- No personal data is stored permanently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is for educational purposes only. Please respect Spotify's Terms of Service and copyright laws. Only download content you have the right to access.

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the setup instructions
3. Check your configuration
4. Open an issue on GitHub with detailed error logs

---

**Made with ❤️ for music lovers everywhere**
