# 🎵 Spotify Downloader Bot

<p align="center">
  <a href="#"><img src="https://badges.strrl.dev/visits/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&label=Visits&logo=github" alt="Visits badge" /></a>
  <a href="#"><img src="https://img.shields.io/github/stars/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=EEAA00&label=Stars&logo=github" alt="Stars badge" /></a>
  <a href="#"><img src="https://img.shields.io/github/repo-size/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=007BFF&label=Repo%20Size&logo=github" alt="Repo size badge" /></a>
</p>

<div align="center">

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge\&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge\&logo=python)
![Spotify](https://img.shields.io/badge/Spotify-Downloader-green?style=for-the-badge\&logo=spotify)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A production-ready, scalable Telegram bot for downloading music from Spotify with advanced features.**

[🚀 Quick Start](#-quick-start) • [🛠️ Setup](#️-installation--setup) • [📖 Documentation](#-documentation)

</div>


## ✨ Features

### 🎵 Core

* **Multi-format downloads**: Tracks, albums, playlists
* **Quality selection**: 128 kbps / 320 kbps
* **Metadata extraction**: Artist, title, album
* **Progress updates**: Real-time status messages
* **Smart validation**: Strict Spotify URL checks

### 🛡️ Production

* **Rate limiting**: Flood protection (default: 5 requests / 60s)
* **Error handling**: Robust recovery with helpful messages
* **Logging**: Structured logging with rotation
* **Config management**: Environment-driven settings
* **Dependencies**: Automatic FFmpeg installation

### 🌐 UX

* **Multilingual**: English & Persian (Farsi)
* **Commands**: `/start`, `/help`
* **Inline UI**: Quality selector keyboards
* **File hygiene**: Auto-cleanup & size limits

### 🔧 Developer

* **Modular architecture**
* **Type hints** throughout
* **Well-documented code**
* **Extensible** for new features

> **Important:** Before running the bot, verify Spotify API connectivity with **[Spotify-API-Test](https://github.com/power0matin/Spotify-API-Test)**.


## 🚀 Quick Start

### Prerequisites

* **Python 3.8+**
* **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
* **Git**
* **Ubuntu/Debian** (for automatic FFmpeg installation)

### 1) Clone & Setup

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2) Configuration

```bash
export BOT_TOKEN="your_bot_token_here"

# Optional tweaks
export RATE_LIMIT_REQUESTS="5"
export RATE_LIMIT_WINDOW_SECONDS="60"
export DEFAULT_QUALITY="320"
export MAX_DOWNLOAD_SIZE_MB="50"
export LOG_LEVEL="INFO"
```

### 3) Run

```bash
python bot.py
```


## 🛠️ Installation & Setup

### Environment Variables

| Variable                    | Description                            | Default     |
| --------------------------- | -------------------------------------- | ----------- |
| `BOT_TOKEN`                 | **Required** — Telegram bot token      | —           |
| `DOWNLOAD_DIR`              | Storage directory for downloads        | `downloads` |
| `QUEUE_DIR`                 | Directory for queue files              | `queue`     |
| `MAX_DOWNLOAD_SIZE_MB`      | Max file size (MB)                     | `50`        |
| `RATE_LIMIT_REQUESTS`       | Max requests per window                | `5`         |
| `RATE_LIMIT_WINDOW_SECONDS` | Window length (seconds)                | `60`        |
| `DEFAULT_QUALITY`           | Default audio quality (`128` or `320`) | `320`       |
| `LOG_LEVEL`                 | Logging level                          | `INFO`      |
| `SUPPORTED_LANGUAGES`       | Comma-separated locale list            | `en,fa`     |
| `DEFAULT_LANGUAGE`          | Default locale                         | `en`        |


## 🚀 Production Deployment

### Systemd (Recommended)

```bash
sudo cp systemd/spotify-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable spotify-bot
sudo systemctl start spotify-bot
```

Check status/logs:

```bash
sudo systemctl status spotify-bot
sudo journalctl -u spotify-bot -f
```

### Docker

```bash
# Build
docker build -t spotify-bot .

# Run
docker run -d \
  --name spotify-bot \
  -e BOT_TOKEN="your_token_here" \
  -v "$(pwd)"/downloads:/app/downloads \
  -v "$(pwd)"/logs:/app/logs \
  spotify-bot
```


## 📖 Documentation

### Project Structure

```
├── bot.py                     # Entry point
├── config.py                  # Configuration manager
├── requirements.txt
├── handlers/
│   ├── command_handler.py     # /start, /help
│   ├── spotify_handler.py     # URL processing
│   └── callback_handler.py    # Inline callbacks
├── utils/
│   ├── downloader.py          # Download engine
│   ├── spotify_utils.py       # URL validation & metadata
│   ├── rate_limiter.py        # Throttling
│   ├── i18n.py                # Internationalization
│   ├── logging_config.py      # Logging setup
│   └── queue_functions.py     # Queue ops
├── systemd/
├── scripts/
└── docs/
```

### API Reference (Internal)

**Core Classes**

* `SpotifyBot` — lifecycle & orchestration
* `SpotifyDownloader` — high-level download engine
* `RateLimiter` — user throttling
* `Messages` — multilingual text provider
* `SpotifyURLValidator` — URL parsing/validation

**Key Functions**

* `download_and_send()` — Orchestrates end-to-end flow
* `validate_spotify_url()` — Ensures supported URL types
* `get_spotify_metadata()` — Fetches metadata
* `check_rate_limit()` — Enforces throttling

### Supported Spotify URLs

```
# Direct
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3
https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd

# With params (cleaned automatically)
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh?si=abc123

# URI format
spotify:track:4iV5W9uYEdYUVa79Axb7Rh
spotify:album:1DFixLWuPkv3KT3TnV35m3

# Regional
https://open.spotify.com/de/track/4iV5W9uYEdYUVa79Axb7Rh
```


## 🔧 Advanced Configuration

### Custom Messages

```python
# utils/i18n.py
TRANSLATIONS = {
  "en": {
    "welcome": "Your custom welcome message",
    "help": "Your custom help text",
  }
}
```

### Rate Limiting

```python
from utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter(
    max_requests=10,
    window_seconds=120
)
```

### Logging

```bash
export LOG_LEVEL="DEBUG"      # DEBUG, INFO, WARNING, ERROR
export LOG_FILE="custom.log"
```


## 🐛 Troubleshooting

**FFmpeg not found**

```bash
sudo apt update && sudo apt install ffmpeg
```

**Permission denied**

```bash
chmod +x start_bot.sh
chown -R $USER:$USER downloads/ logs/
```

**Too many requests**

* Increase `RATE_LIMIT_REQUESTS`
* Or reduce `RATE_LIMIT_WINDOW_SECONDS`

**High memory usage**

* Lower `MAX_DOWNLOAD_SIZE_MB`
* Enable log rotation

**Debug mode**

```bash
export LOG_LEVEL="DEBUG"
python bot.py
```

**Tail logs**

```bash
tail -f logs/spotify_bot.log
grep "ERROR" logs/spotify_bot.log
grep "Download" logs/spotify_bot.log
```


## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a PR

**Dev setup**

```bash
pip install -r requirements.txt
export LOG_LEVEL="DEBUG"
python bot.py
# Tests (when available)
pytest tests/
```


## 📜 License

MIT — see [LICENSE](LICENSE).


## ⚠️ Disclaimer

This bot is for educational use only. You are responsible for complying with Spotify’s Terms of Service and copyright laws. The authors assume no liability for misuse.


## 📞 Support

* 🐛 Issues: [https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
* 📧 Email: [power0matin@gmail.com](mailto:power0matin@gmail.com)
* 💬 Telegram: [@power0matin](https://t.me/power0matin)


<div align="center">

**Made with ❤️ by [power0matin](https://github.com/power0matin)**
⭐ If this project helps you, **please star the repo**!

</div>


