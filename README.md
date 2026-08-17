# 🎵 Spotify Downloader Bot

<!-- repo-badges:start -->
<p align="center">
  <a href="https://hits.sh/github.com/power0matin/Telegram-Music-Downloader-Bot/"><img src="https://hits.sh/github.com/power0matin/Telegram-Music-Downloader-Bot.svg?style=flat-square&amp;label=Views&amp;labelColor=18181B&amp;color=0EA5E9&amp;logo=github" alt="Repository Views"/></a>
  <a href="https://github.com/power0matin/Telegram-Music-Downloader-Bot/stargazers"><img src="https://img.shields.io/github/stars/power0matin/Telegram-Music-Downloader-Bot?style=flat-square&amp;label=Stars&amp;labelColor=18181B&amp;color=F59E0B&amp;logo=github&amp;logoColor=white" alt="GitHub Stars"/></a>
  <a href="https://github.com/power0matin/Telegram-Music-Downloader-Bot/forks"><img src="https://img.shields.io/github/forks/power0matin/Telegram-Music-Downloader-Bot?style=flat-square&amp;label=Forks&amp;labelColor=18181B&amp;color=6366F1&amp;logo=github&amp;logoColor=white" alt="GitHub Forks"/></a>
  <a href="https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues"><img src="https://img.shields.io/github/issues/power0matin/Telegram-Music-Downloader-Bot?style=flat-square&amp;label=Issues&amp;labelColor=18181B&amp;color=22C55E&amp;logo=github&amp;logoColor=white" alt="GitHub Issues"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/power0matin/Telegram-Music-Downloader-Bot?style=flat-square&amp;label=License&amp;labelColor=18181B&amp;color=EF4444&amp;logo=github&amp;logoColor=white" alt="GitHub License"/></a>
</p>
<!-- repo-badges:end -->

<p align="center">
  <a href="#"><img src="https://img.shields.io/github/stars/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=EEAA00&label=Stars&logo=github" alt="Stars badge" /></a>
  <a href="#"><img src="https://img.shields.io/github/repo-size/power0matin/Telegram-Music-Downloader-Bot?style=flat&labelColor=333333&logoColor=E7E7E7&color=007BFF&label=Repo%20Size&logo=github" alt="Repo size badge" /></a>
</p>

<div align="center">

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge\&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.10--3.14-blue?style=for-the-badge\&logo=python)
![Spotify](https://img.shields.io/badge/Spotify-Downloader-green?style=for-the-badge\&logo=spotify)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A Telegram bot that matches Spotify metadata to downloadable audio and sends the result back to the requesting chat.**

[🚀 Quick Start](#-quick-start) • [🛠️ Setup](#️-installation--setup) • [📖 Documentation](#-documentation)

</div>


## ✨ Features

### 🎵 Core

* **Spotify content types**: Tracks, albums, playlists
* **MP3 bitrate selection**: 128 kbps / 320 kbps
* **Metadata extraction**: Artist, title, album
* **Status updates**: Download state and delivery feedback
* **Smart validation**: Strict Spotify URL checks

> **Audio quality note:** 320 kbps selects the MP3 output bitrate. It cannot
> create source quality that the selected audio provider does not supply.

### 🛡️ Production

* **Rate limiting**: Flood protection (default: 20 requests / 60s)
* **Error handling**: Robust recovery with helpful messages
* **Logging**: Structured logging with rotation
* **Config management**: Environment-driven settings
* **Dependencies**: Verified FFmpeg + spotDL 4.5.x compatibility

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

## 🚀 Quick Start

### Prerequisites

* **Python 3.10–3.14** (required by spotDL 4.5.x)
* **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
* **Git**
* **FFmpeg**
* **Ubuntu 22.04/24.04** for the automated VPS installer

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
export RATE_LIMIT_REQUESTS="20"
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
| `QUEUE_PATH`                | Queue tracking file                     | `queue/queue.json` |
| `MAX_DOWNLOAD_SIZE_MB`      | Max file size (MB)                     | `50`        |
| `RATE_LIMIT_REQUESTS`       | Max requests per window                | `20`        |
| `RATE_LIMIT_WINDOW_SECONDS` | Window length (seconds)                | `60`        |
| `DEFAULT_QUALITY`           | Default audio quality (`128` or `320`) | `320`       |
| `LOG_LEVEL`                 | Logging level                          | `INFO`      |
| `DEFAULT_LANGUAGE`          | Default locale                         | `en`        |
| `DOWNLOAD_TIMEOUT_SECONDS`  | Per-attempt spotDL timeout              | `900`       |
| `UPLOAD_TIMEOUT_SECONDS`    | Telegram audio upload timeout           | `180`       |
| `UPLOAD_RETRIES`            | Transient Telegram upload attempts      | `3`         |
| `MAX_CONCURRENT_DOWNLOADS`  | Global concurrent download limit        | `3`         |
| `AUDIO_PROVIDERS`           | spotDL provider fallback order          | `soundcloud,youtube-music,youtube` |
| `COOKIE_FILE`               | Optional Netscape cookies file for yt-dlp | —         |
| `PROXY_URL`                 | Optional HTTP(S) proxy for audio providers | —        |
| `YTDLP_EXTRA_ARGS`          | Optional raw yt-dlp arguments passed by spotDL | —    |


## 🚀 Production Deployment

### Systemd (Recommended)

On Ubuntu 22.04/24.04, the installer creates the dedicated service user,
runtime directories, Deno fallback runtime, environment file, and hardened
systemd unit:

```bash
chmod +x setup_vps.sh
sudo ./setup_vps.sh
```

Check status/logs:

```bash
sudo systemctl status spotify-bot
sudo journalctl -u spotify-bot -f
```


## 📖 Documentation

### Project Structure

```
├── bot.py                     # Entry point
├── config.py                  # Configuration manager
├── requirements.txt
├── requirements-dev.txt
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
├── tests/
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

Edit the `Messages.TRANSLATIONS` mapping in `utils/i18n.py`; keep the same
message keys in both `en` and `fa` so every handler has a valid fallback.

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
export LOG_LEVEL="DEBUG"      # DEBUG, INFO, WARNING, ERROR, CRITICAL
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
pip install -r requirements-dev.txt
export LOG_LEVEL="DEBUG"
python bot.py
pytest -q
```


## 📜 License

MIT — see [LICENSE](LICENSE).


## ⚠️ Disclaimer

This bot is for educational use only. You are responsible for complying with Spotify’s Terms of Service and copyright laws. The authors assume no liability for misuse.


## 📬 Contact & Support

**Matin Shahabadi (متین شاه‌آبادی / متین شاه آبادی)**

* 🐛 Issues: [https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
* 💬 Telegram: [@power0matin](https://t.me/power0matin)
* 🌐 Website: [matinshahabadi.ir](https://matinshahabadi.ir)
* 📧 Email: [me@matinshahabadi.ir](mailto:me@matinshahabadi.ir)
* 🧑‍💻 GitHub: [power0matin](https://github.com/power0matin)
* 💼 LinkedIn: [matin-shahabadi](https://www.linkedin.com/in/matin-shahabadi)


<div align="center">

**Made with ❤️ by [power0matin](https://github.com/power0matin)**
⭐ If this project helps you, **please star the repo**!

</div>
