# 🎵 Spotify Downloader Bot

<p align="center">
  <a href="#">
        <img src="https://badges.strrl.dev/visits/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&label=Visits&logo=github" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/github/stars/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=EEAA00&label=Stars&logo=github"/>
  </a>
  <a href="#">
  <img src="https://img.shields.io/github/repo-size/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=007BFF&label=Repo%20Size&logo=github"/>
  </a>
  <a href="#">
  <img src="https://img.shields.io/github/stars/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=007BFF&label=Stars&logo=github"/>
  </a>
</p>

<div align="center">

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Spotify](https://img.shields.io/badge/Spotify-Downloader-green?style=for-the-badge&logo=spotify)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A production-ready, scalable Telegram bot for downloading music from Spotify with advanced features**

[🚀 Quick Start](#quick-start) • [🛠️ Setup](#installation--setup) • [📖 Documentation](#documentation)

</div>

---

## ✨ Features

### 🎵 **Core Features**

- **Multi-format Downloads**: Tracks, albums, and playlists
- **Quality Selection**: 128 kbps and 320 kbps options
- **Metadata Extraction**: Artist names, track titles, album info
- **Progress Updates**: Real-time download status messages
- **Smart Validation**: Comprehensive Spotify URL validation

### 🛡️ **Production Features**

- **Rate Limiting**: Configurable flood protection (5 requests/60s default)
- **Error Handling**: Robust error recovery with user-friendly messages
- **Logging System**: Comprehensive logging with rotation
- **Configuration Management**: Environment-based configuration
- **Dependency Management**: Automatic FFmpeg installation

### 🌐 **User Experience**

- **Multilingual Support**: English and Persian (Farsi)
- **Command Support**: `/start`, `/help` commands
- **Interactive Interface**: Inline keyboards for quality selection
- **File Management**: Automatic cleanup and size limits

### 🔧 **Developer Features**

- **Modular Architecture**: Clean separation of concerns
- **Type Hints**: Full type annotation support
- **Documentation**: Comprehensive code documentation
- **Extensible Design**: Easy to add new features
  
> ### ⚠️ Important: Run Spotify API Test Script Before Using the Bot
> Before running the bot, please run the [Spotify-API-Test](https://github.com/power0matin/Spotify-API-Test) script to verify your Spotify API connectivity.


<a name="quick-start"></a>

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- A **Telegram Bot Token** (get one from [@BotFather](https://t.me/BotFather))
- **Git** for cloning the repository
- **Ubuntu/Debian** system (for automatic FFmpeg installation)

### 1. Clone and Setup

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Set your bot token
export BOT_TOKEN="your_bot_token_here"

# Optional: Customize configuration
export RATE_LIMIT_REQUESTS="5"
export RATE_LIMIT_WINDOW_SECONDS="60"
export DEFAULT_QUALITY="320"
export MAX_DOWNLOAD_SIZE_MB="50"
export LOG_LEVEL="INFO"
```

### 3. Run the Bot

```bash
python bot.py
```

## 🛠️ Installation & Setup

### Environment Variables

| Variable                    | Description                       | Default     |
| --------------------------- | --------------------------------- | ----------- |
| `BOT_TOKEN`                 | **Required** - Telegram bot token | -           |
| `DOWNLOAD_DIR`              | Directory for downloads           | `downloads` |
| `QUEUE_DIR`                 | Directory for queue files         | `queue`     |
| `MAX_DOWNLOAD_SIZE_MB`      | Max file size in MB               | `50`        |
| `RATE_LIMIT_REQUESTS`       | Max requests per window           | `5`         |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window in seconds      | `60`        |
| `DEFAULT_QUALITY`           | Default audio quality (128/320)   | `320`       |
| `LOG_LEVEL`                 | Logging level                     | `INFO`      |
| `SUPPORTED_LANGUAGES`       | Comma-separated languages         | `en,fa`     |
| `DEFAULT_LANGUAGE`          | Default language                  | `en`        |

### Production Deployment

#### Using Systemd (Recommended)

1. Create a service file:

```bash
sudo cp systemd/spotify-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable spotify-bot
sudo systemctl start spotify-bot
```

2. Check status:

```bash
sudo systemctl status spotify-bot
sudo journalctl -u spotify-bot -f  # View logs
```

#### Using Docker

```bash
# Build image
docker build -t spotify-bot .

# Run container
docker run -d \
  --name spotify-bot \
  -e BOT_TOKEN="your_token_here" \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/logs:/app/logs \
  spotify-bot
```

## 📖 Documentation

### Project Structure

```
├── bot.py                      # Main bot entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── handlers/                   # Message and callback handlers
│   ├── command_handler.py      # /start, /help commands
│   ├── spotify_handler.py      # Spotify URL processing
│   └── callback_handler.py     # Inline keyboard callbacks
├── utils/                      # Utility modules
│   ├── downloader.py          # Enhanced download engine
│   ├── spotify_utils.py       # URL validation & metadata
│   ├── rate_limiter.py        # Rate limiting system
│   ├── i18n.py               # Internationalization
│   ├── logging_config.py     # Logging configuration
│   └── queue_functions.py    # Queue management
├── systemd/                   # Systemd service files
├── scripts/                   # Deployment scripts
└── docs/                      # Additional documentation
```

### API Reference

#### Core Classes

- `SpotifyBot`: Main bot class with lifecycle management
- `SpotifyDownloader`: Enhanced download engine
- `RateLimiter`: User rate limiting system
- `Messages`: Multilingual message system
- `SpotifyURLValidator`: URL validation and parsing

#### Key Functions

- `download_and_send()`: Main download orchestrator
- `validate_spotify_url()`: URL validation
- `get_spotify_metadata()`: Metadata extraction
- `check_rate_limit()`: Rate limit verification

### Supported Spotify URLs

The bot supports various Spotify URL formats:

```
# Direct URLs
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3
https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd

# Sharing URLs (automatically cleaned)
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh?si=abc123

# Spotify URIs
spotify:track:4iV5W9uYEdYUVa79Axb7Rh
spotify:album:1DFixLWuPkv3KT3TnV35m3

# Regional URLs
https://open.spotify.com/de/track/4iV5W9uYEdYUVa79Axb7Rh
```

## 🔧 Advanced Configuration

### Custom Message Templates

Modify messages in `utils/i18n.py` to customize bot responses:

```python
TRANSLATIONS = {
    'en': {
        'welcome': "Your custom welcome message",
        'help': "Your custom help text",
        # ... other messages
    }
}
```

### Rate Limiting Configuration

```python
# Custom rate limiter
from utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter(
    max_requests=10,      # 10 requests
    window_seconds=120    # per 2 minutes
)
```

### Logging Configuration

```bash
# Environment variables for logging
export LOG_LEVEL="DEBUG"        # DEBUG, INFO, WARNING, ERROR
export LOG_FILE="custom.log"    # Custom log file name
```

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

2. **Permission denied errors**

   ```bash
   chmod +x start_bot.sh
   chown -R $USER:$USER downloads/ logs/
   ```

3. **Rate limiting issues**

   - Increase `RATE_LIMIT_REQUESTS`
   - Decrease `RATE_LIMIT_WINDOW_SECONDS`

4. **Memory issues**
   - Reduce `MAX_DOWNLOAD_SIZE_MB`
   - Enable log rotation

### Debug Mode

```bash
export LOG_LEVEL="DEBUG"
python bot.py
```

### Monitoring

Check logs for issues:

```bash
# View real-time logs
tail -f logs/spotify_bot.log

# Search for errors
grep "ERROR" logs/spotify_bot.log

# Monitor downloads
grep "Download" logs/spotify_bot.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
export LOG_LEVEL="DEBUG"
python bot.py

# Run tests (when available)
pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is for educational purposes only. Users are responsible for complying with Spotify's Terms of Service and applicable copyright laws. The developers are not responsible for any misuse of this software.

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- 📧 **Contact**: [Email](mailto:power0matin@gmail.com)
- 💬 **Telegram**: [@power0matin](https://t.me/power0matin)

---

<div align="center">

**Made with ❤️ by [power0matin](https://github.com/power0matin)**

⭐ **If you found this project helpful, please give it a star!** ⭐

</div>
