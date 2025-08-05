# 🎵 Telegram Spotify Downloader Bot

<div align="center">

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Spotify](https://img.shields.io/badge/Spotify-Downloader-green?style=for-the-badge&logo=spotify)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A powerful and user-friendly Telegram bot for downloading music from Spotify**

[🇫🇦 فارسی](Documentation files/README.fa.md)  • [🚀 Quick Start](#quick-start) • [🛠️ Setup](#installation--setup)

</div>

---

## ✨ Features

- 🎵 **Multi-format Downloads**: Download individual tracks, full albums, and playlists
- 🔊 **Quality Selection**: Choose between 128 kbps and 320 kbps audio quality
- 🤖 **Interactive Interface**: User-friendly buttons and real-time progress updates
- 🛡️ **Robust Error Handling**: Comprehensive validation and helpful error messages
- 🗂️ **Smart File Management**: Automatic cleanup and organized downloads
- ⚡ **High Performance**: Retry logic, rate limiting, and optimized downloads
- 🔧 **Easy Deployment**: One-script setup with automatic dependency management
- 🌐 **Multi-language Support**: English and Persian documentation

<a name="quick-start"></a>
## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- A **Telegram Bot Token** (get one from [@BotFather](https://t.me/BotFather))
- **Git** for cloning the repository
- Internet connection for downloading dependencies

### 1. Clone the Repository

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your Bot Token

Choose one of these methods:

**Method 1: Environment Variable**
```bash
export BOT_TOKEN="your_bot_token_here"
```

**Method 2: Create .env file**
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

**Method 3: Create config.py**
```bash
cp config.example.py config.py
# Then edit config.py and add your token
```

### 5. Start the Bot

**Using the startup script (recommended):**
```bash
chmod +x start_bot.sh
./start_bot.sh
```

**Or manually:**
```bash
python3 bot.py
```

<a name="installation--setup"></a>
## 🛠️ Installation & Setup

### Getting Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### System Dependencies

The bot will automatically install FFmpeg if it's missing. For manual installation:

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg website](https://ffmpeg.org/download.html) or use package managers like Chocolatey.

### Configuration Options

Create a `config.py` file for advanced configuration:

```python
# Required
BOT_TOKEN = 'your_bot_token_here'

# Optional settings
MAX_DOWNLOAD_SIZE = 50  # MB
DOWNLOAD_TIMEOUT = 300  # seconds
CLEANUP_INTERVAL = 3600  # seconds
SUPPORTED_FORMATS = ['mp3', 'flac', 'ogg']
```

## 📱 How to Use

### Basic Usage

1. **Start the bot**: Send `/start` to your bot
2. **Send a Spotify link**: Copy any Spotify URL and send it to the bot
3. **Choose quality**: Select either 128 kbps or 320 kbps
4. **Download**: Wait for your music to be processed and sent

### Supported URL Types

- **🎵 Tracks**: `https://open.spotify.com/track/...`
- **💿 Albums**: `https://open.spotify.com/album/...`
- **📜 Playlists**: `https://open.spotify.com/playlist/...`

### Example Workflow

```
User: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
Bot: 🎵 Found: "Never Gonna Give You Up" by Rick Astley
     Choose your preferred quality:
     [128 kbps] [320 kbps]

User: [Clicks 320 kbps]
Bot: ⬇️ Downloading...
     ✅ Download complete! Sending file...
     [Audio file sent]
```

## 🏗️ Project Structure

```
Telegram-Music-Downloader-Bot/
├── 🤖 bot.py                      # Main bot entry point
├── ⚙️ config.example.py          # Example config (env-based settings)
├── 📋 requirements.txt            # Python dependencies
├── 🚀 start_bot.sh               # Startup script
├── 📁 handlers/                  # Bot message handlers
│   ├── __init__.py
│   ├── spotify_handler.py         # Spotify URL processing
│   └── callback_handler.py        # Button interactions
├── 🛠️ utils/                     # Utility modules
│   ├── __init__.py
│   ├── downloader.py              # Download logic
│   ├── queue_functions.py         # Queue management
│   └── variables.py               # Global/shared variables
├── 📂 scripts/                   # Maintenance shell scripts
│   ├── cleanup_processes.sh       # Kills stray download processes
│   └── restart_bot.sh             # Restarts the bot
├── 📂 systemd/                   # Systemd service definitions
│   └── telegram_bot.service       # Service unit file
├── 📂 .github/workflows/         # GitHub Actions workflows
│   └── (your CI/CD YAML files here)
├── 📂 queue/                     # Queue storage (auto-created)
├── ⬇️ downloads/                 # Temporary downloads (auto-created)
├── 📚 Documentation files        # Project documentation
│   ├── README.md                  # English documentation
│   ├── README.fa.md               # Persian documentation
│   ├── SETUP_INSTRUCTIONS.md      # Installation & setup guide
│   └── FIXES_APPLIED.md           # Summary of fixes
├── 🧾 .gitignore                 # Git ignored files
├── 🪪 LICENSE                    # Project license

```

## 🔧 Troubleshooting

### Common Issues

**1. "BOT_TOKEN not set"**
```bash
# Solution: Set your bot token
export BOT_TOKEN="your_token_here"
```

**2. "FFmpeg not found"**
```bash
# Solution: Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

**3. "Module not found" errors**
```bash
# Solution: Activate virtual environment and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

**4. Download failures**
- ✅ Verify the Spotify URL is valid and public
- ✅ Check your internet connection
- ✅ Some content may be geo-restricted or unavailable

**5. Permission errors**
```bash
# Solution: Make scripts executable
chmod +x start_bot.sh
```

### Debug Mode

Run with verbose logging:
```bash
python3 bot.py --debug
```

### Getting Help

- 📖 Check the [Setup Instructions](SETUP_INSTRUCTIONS.md)
- 🐛 Report bugs in [Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- 💡 Request features via [Discussions](https://github.com/power0matin/Telegram-Music-Downloader-Bot/discussions)

## 🔒 Security & Privacy

- ✅ **No data collection**: The bot doesn't store user data or download history
- ✅ **Secure token handling**: Bot tokens are stored securely via environment variables
- ✅ **Automatic cleanup**: Temporary files are automatically deleted after sending
- ✅ **Rate limiting**: Built-in protection against spam and abuse

## 🚀 Deployment Options

### Local Development
```bash
./start_bot.sh
```

### Production Deployment

**Using systemd (Linux):**
```bash
# Copy the service file
sudo cp systemd/spotify-bot.service /etc/systemd/system/
sudo systemctl enable spotify-bot
sudo systemctl start spotify-bot
```

**Using Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
```

**Using PM2:**
```bash
npm install -g pm2
pm2 start bot.py --interpreter python3 --name spotify-bot
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🍴 Fork** the repository
2. **🌟 Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **💾 Commit** your changes: `git commit -m 'Add amazing feature'`
4. **📤 Push** to the branch: `git push origin feature/amazing-feature`
5. **🔄 Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot

# Create development environment
python3 -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install black pylint pytest

# Run tests
python3 -m pytest tests/
```

## 📊 Performance

- ⚡ **Fast downloads**: Optimized for speed with parallel processing
- 💾 **Memory efficient**: Smart memory management for large files
- 🔄 **Retry logic**: Automatic retry on temporary failures
- 📈 **Scalable**: Designed to handle multiple concurrent users

## 📋 Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: For audio processing (auto-installed)
- **SpotDL**: 4.2.1+ (included in requirements)
- **Storage**: At least 100MB free space for temporary files

## 📞 Support

- 🆘 **Issues**: [GitHub Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/power0matin/Telegram-Music-Downloader-Bot/discussions)
- 📧 **Email**: [Contact maintainer](mailto:power0matin@example.com)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SpotDL**: For the excellent Spotify downloading library
- **pyTelegramBotAPI**: For the robust Telegram bot framework
- **Contributors**: Thanks to everyone who has contributed to this project

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ by the open-source community

</div>
