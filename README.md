# 🎵 Spotify Downloader Bot

<div align="center">

![Spotify Bot](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

**A powerful Telegram bot that downloads Spotify tracks, albums, and playlists with high-quality audio**

[🚀 Quick Start](#-quick-start) • [📖 Full Guide](#-complete-installation-guide) • [🎯 Usage](#-usage) • [🔧 Troubleshooting](#-troubleshooting)

---

</div>

## ✨ Features

🎵 **Complete Spotify Support**
- Download individual tracks
- Download full albums
- Download entire playlists
- Support for all public Spotify content

🎚️ **Quality Options**
- 128 kbps (smaller files, faster downloads)
- 320 kbps (high quality, larger files)

🤖 **User-Friendly Interface**
- Interactive quality selection buttons
- Real-time progress updates
- Helpful error messages with emojis
- Clean and intuitive commands

🛡️ **Reliable & Secure**
- Automatic retry mechanism for failed downloads
- Rate limiting protection
- Secure token handling
- Automatic file cleanup
- User-isolated download directories

⚡ **Easy Setup**
- One-command automatic installation
- Cross-platform support (Linux, macOS, Windows)
- Virtual environment management
- Dependency auto-installation

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/spotify-downloader-bot.git
cd spotify-downloader-bot

# Run the automatic setup (installs everything)
./setup_bot.sh
```

### Option 2: Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

```bash
# Clone the repository
git clone https://github.com/your-username/spotify-downloader-bot.git
cd spotify-downloader-bot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure your bot token
cp .env.example .env
# Edit .env and add your bot token

# Start the bot
./start_bot.sh
```

</details>

## 📖 Complete Installation Guide

### Step 1: Prerequisites

Before starting, make sure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Internet connection** for downloading dependencies
- **Telegram account** to create a bot

### Step 2: Get Telegram Bot Token

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** and send `/newbot`
3. **Choose a name** for your bot (e.g., "My Music Bot")
4. **Choose a username** (must end with 'bot', e.g., "my_music_downloader_bot")
5. **Copy the token** that BotFather gives you (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. **Keep this token secure** - never share it publicly!

### Step 3: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/spotify-downloader-bot.git
cd spotify-downloader-bot

# Make setup script executable
chmod +x setup_bot.sh

# Run automatic setup
./setup_bot.sh
```

The setup script will:
- ✅ Check system requirements
- ✅ Install system dependencies (FFmpeg, etc.)
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Create configuration files
- ✅ Set up directory structure
- ✅ Verify installation

### Step 4: Configure Bot Token

During setup, you'll be prompted to enter your bot token. You can also configure it manually:

```bash
# Edit the .env file
nano .env

# Add your token
BOT_TOKEN=your_telegram_bot_token_here
```

### Step 5: Start the Bot

```bash
# Start the bot
./start_bot.sh
```

You should see:
```
🤖 Starting Spotify Downloader Bot...
Bot is running...
```

### Step 6: Test Your Bot

1. **Find your bot** on Telegram (search for the username you created)
2. **Send `/start`** to begin
3. **Send a Spotify link** (e.g., `https://open.spotify.com/track/...`)
4. **Choose quality** using the buttons
5. **Receive your music!** 🎵

## 🎯 Usage

### Supported Spotify URLs

| Type | Example URL | Description |
|------|-------------|-------------|
| **Track** | `https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh` | Single song |
| **Album** | `https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3` | Complete album |
| **Playlist** | `https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd` | User playlist |

### How to Use

1. **Start the bot**: `./start_bot.sh`
2. **Open Telegram** and find your bot
3. **Send a Spotify link** to the bot
4. **Select quality**:
   - 🎵 **128 kbps** - Smaller files, faster downloads
   - 🎶 **320 kbps (HQ)** - Higher quality, larger files
5. **Wait for download** and receive your files!

### Bot Commands

| Command | Description |
|---------|-------------|
| Send any Spotify URL | Start download process |
| Quality buttons | Select audio quality |

## 🔧 Troubleshooting

### Common Issues and Solutions

<details>
<summary><strong>🚫 "No module named 'telebot'"</strong></summary>

**Problem**: Python dependencies not installed or virtual environment not activated.

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>🚫 "BOT_TOKEN not set"</strong></summary>

**Problem**: Telegram bot token not configured.

**Solution**:
```bash
# Edit .env file
nano .env

# Add your token
BOT_TOKEN=your_actual_bot_token_here
```

</details>

<details>
<summary><strong>🚫 "FFmpeg not found"</strong></summary>

**Problem**: FFmpeg not installed on system.

**Solution**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS
brew install ffmpeg

# Or run setup script again
./setup_bot.sh
```

</details>

<details>
<summary><strong>🚫 "Permission denied" for scripts</strong></summary>

**Problem**: Scripts don't have execute permissions.

**Solution**:
```bash
chmod +x setup_bot.sh
chmod +x start_bot.sh
```

</details>

<details>
<summary><strong>🚫 Download failures</strong></summary>

**Problem**: Downloads failing or timing out.

**Solutions**:
- ✅ Check internet connection
- ✅ Verify Spotify URL is correct and public
- ✅ Wait a few minutes (rate limiting)
- ✅ Try a different track/album
- ✅ Check if content is geo-restricted

</details>

### Advanced Troubleshooting

**View bot logs**:
```bash
# Real-time logs
tail -f logs/bot.log

# All logs
cat logs/bot.log
```

**Restart bot**:
```bash
# Stop bot (Ctrl+C) then restart
./start_bot.sh
```

**Complete reinstall**:
```bash
# Remove virtual environment
rm -rf venv

# Run setup again
./setup_bot.sh
```

### Getting Help

If you're still having issues:

1. **Check the logs** for detailed error messages
2. **Verify your configuration** in `.env` file
3. **Test with simple Spotify track** first
4. **Check system requirements** are met
5. **Open an issue** on GitHub with error logs

## 📁 Project Structure

```
spotify-downloader-bot/
├── 🤖 bot.py                    # Main bot application
├── ⚙️ config.py                 # Configuration management
├── 📦 requirements.txt          # Python dependencies
├── 🛠️ setup_bot.sh             # Automatic setup script
├── 🚀 start_bot.sh             # Bot startup script
├── 📝 .env                     # Configuration file (create this)
├── 📖 README.md                # English documentation
├── 📖 README.fa.md             # Persian documentation
├── 📁 handlers/                # Message handling
│   ├── __init__.py
│   ├── spotify_handler.py      # Main message processing
│   └── callback_handler.py     # Button interactions
├── 📁 utils/                   # Utility functions
│   ├── __init__.py
│   ├── downloader.py           # Download functionality
│   ├── queue_functions.py      # Queue management
│   └── variables.py            # Path configurations
├── 📁 venv/                    # Python virtual environment
├── 📁 queue/                   # Download queue storage
├── 📁 downloads/               # Temporary downloads
└── 📁 logs/                    # Application logs
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to customize:

```env
# Required: Your Telegram bot token
BOT_TOKEN=your_telegram_bot_token_here

# Optional: Default quality (128 or 320)
DEFAULT_QUALITY=320

# Optional: Maximum download retries
MAX_RETRIES=5

# Optional: Retry delay in seconds
RETRY_DELAY=5
```

### Advanced Configuration

Edit `config.py` for advanced settings:
- Download directories
- Timeout settings
- Error handling behavior
- Queue management

## 🔒 Security & Privacy

- **🔐 Token Security**: Bot tokens are stored securely in environment variables
- **🗂️ File Management**: Downloaded files are automatically cleaned up
- **👤 User Isolation**: Each user has separate download directories
- **🚫 No Data Storage**: No personal information is permanently stored
- **🛡️ Input Validation**: All URLs are validated before processing

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/spotify-downloader-bot.git
cd spotify-downloader-bot

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Disclaimer

This bot is for **educational purposes only**. Please respect:
- Spotify's Terms of Service
- Copyright laws in your jurisdiction
- Artist and label rights

Only download content you have the legal right to access.

## 🆘 Support & Community

### Quick Help
- 📖 **Documentation**: Check this README first
- 🔧 **Troubleshooting**: See the troubleshooting section above
- 📝 **Configuration**: Review the configuration section

### Get Support
- 🐛 **Bug Reports**: [Open an issue](https://github.com/your-username/spotify-downloader-bot/issues)
- 💡 **Feature Requests**: [Request a feature](https://github.com/your-username/spotify-downloader-bot/issues)
- ❓ **Questions**: [Ask in discussions](https://github.com/your-username/spotify-downloader-bot/discussions)

### Community
- 🌟 **Star** the repository if you find it useful
- 🔄 **Share** with friends who love music
- 🤝 **Contribute** to make it even better

---

<div align="center">

**Made with ❤️ for music lovers everywhere**

🎵 Happy downloading! 🎵

[⬆️ Back to top](#-spotify-downloader-bot)

</div>
