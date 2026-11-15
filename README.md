# Spotify Link Preview & Optional Audio Delivery Bot

[![CI](https://github.com/power0matin/Telegram-Music-Downloader-Bot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/power0matin/Telegram-Music-Downloader-Bot/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/power0matin/Telegram-Music-Downloader-Bot)](https://github.com/power0matin/Telegram-Music-Downloader-Bot/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11--3.15-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/power0matin/Telegram-Music-Downloader-Bot)](LICENSE)

A Telegram bot that recognizes Spotify track, album, and playlist links. Its default mode shows a best-effort metadata preview and a direct Spotify link. The codebase also includes an optional, permission-gated audio-delivery workflow.

**Default behavior:** preview-only. The bot does not search audio providers, download music, or send audio files in this mode. The optional workflow is not a direct Spotify audio download: it uses spotDL to attempt to find matching recordings on configured third-party providers. Matches and provider availability are not guaranteed.

**Read this in Persian:** [راهنمای فارسی](docs/README.fa.md) · **Need installation help?** [Step-by-step setup guide](docs/SETUP_INSTRUCTIONS.md)

---

## Default behavior

- Recognizes Spotify track, album, and playlist links.
- Validates and normalizes supported Spotify URLs.
- Requests limited metadata from Spotify's official oEmbed endpoint when available.
- Shows a direct link to the Spotify item.
- Supports English and Persian messages, rate limiting, and error handling.
- Does not search third-party audio providers, download audio, or upload audio files to Telegram.
- Does not scrape Spotify embed pages when oEmbed has no metadata.

When Spotify does not return preview information, the bot can still provide the Spotify link.

## Optional audio-file delivery

The audio-delivery workflow is implemented but **disabled by default**. When it is explicitly enabled by an operator who has the required written permissions and licences for the exact workflow:

1. The user sends a supported Spotify track, album, or playlist link.
2. The bot displays available metadata and 128/320 kbps quality choices.
3. spotDL 4.6.0 attempts to find matching audio using the providers listed in AUDIO_PROVIDERS (the sample configuration uses SoundCloud, YouTube Music, and YouTube).
4. The bot validates the resulting local audio files and sends eligible files through Telegram send_audio.

This is not a download from Spotify's audio service. A provider may return no match, a different recording/master, or a partial album/playlist; uploads can also be skipped when a file exceeds the 49,000,000-byte safety limit. Technical availability does not establish permission to download or redistribute content.

To enable this path, both ENABLE_AUTHORIZED_AUDIO_DELIVERY=true and AUDIO_DELIVERY_PERMISSIONS_ACK=true are required. The second flag is only an operator acknowledgement; it grants no permission. Read [COMPLIANCE.md](docs/COMPLIANCE.md) and the [audio-delivery operations guide](docs/AUDIO_DELIVERY.md) before changing either value.

---

## Quick start

Follow these steps to run your own bot. You do not need to edit the Python source code.

### 1. Create a Telegram bot and get its token

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather).
2. Send `/newbot`.
3. Follow the instructions and choose a name and username for your bot.
4. Copy the token BotFather gives you. Keep it private; anyone with this token can control your bot.

You will add this token to the project's `.env` file in step 5.

### 2. Install the prerequisites

You need:

- **Python 3.11, 3.12, 3.13, 3.14, or 3.15**
- **Git**
- An internet connection
- A Telegram account

FFmpeg is **not required** for the default preview-only mode. It is used only by the optional audio-processing path.

**Ubuntu 24.04:** install the local tools with:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

Ubuntu 22.04's default Python is too old for this project. Install Python 3.11–3.15 separately before continuing.

**Windows:** install Python from [python.org](https://www.python.org/downloads/) and Git from [git-scm.com](https://git-scm.com/downloads). During Python setup, enable the option that adds Python to PATH.

**macOS:** install Python 3.11–3.15 from [python.org](https://www.python.org/downloads/). If Git is not installed, macOS may offer to install the Xcode Command Line Tools when you first run `git`.

Check your Python version:

```bash
python --version
```

On some Linux/macOS systems, use `python3 --version`. The version must be between 3.11 and 3.15.

### 3. Download the project

Open Terminal (Linux/macOS) or PowerShell (Windows), then run:

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
```

### 4. Create a virtual environment and install the packages

A virtual environment keeps this project's Python packages separate from other applications on your computer.

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows PowerShell**

First, list the Python versions installed on your computer:

```powershell
py -0p
```

In the example below, replace `3.12` with a Python version between 3.11 and 3.15 that is installed on your computer:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows Command Prompt (CMD)**

```cmd
py -3.12 -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Use the same Python version you selected when creating the virtual environment. When the environment is active, your terminal usually shows `(venv)` at the beginning of the prompt.

### 5. Add your Telegram token

Create a file named `.env` in the project folder by copying the example file.

**Linux / macOS**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Open `.env` with a text editor and replace the example token:

```dotenv
BOT_TOKEN=put_your_real_token_here
DEFAULT_LANGUAGE=fa
ENABLE_AUTHORIZED_AUDIO_DELIVERY=false
AUDIO_DELIVERY_PERMISSIONS_ACK=false
```

- Replace the value of `BOT_TOKEN` with the token from BotFather.
- Set `DEFAULT_LANGUAGE` to `fa` for Persian or `en` for English.
- Keep both audio-delivery flags set to `false`. This is the safe default.

Do not add quotes around the values unless needed, and do not share your token. The `.env` file is excluded by Git, so it should not be committed.

### 6. Start the bot

Make sure the virtual environment is still active, then run:

```bash
python bot.py
```

The bot checks the token with Telegram when it starts. Keep this terminal open while you use the bot. To stop it, press `Ctrl+C`.

On Linux/macOS, you can also use the included helper:

```bash
chmod +x start_bot.sh
./start_bot.sh
```

The helper expects the virtual environment to be in a folder named `venv`. On Windows, use `python bot.py`.

### 7. Try it in Telegram

1. Open the bot you created.
2. Send `/start`.
3. Send `/help` to see the help message.
4. Send a public Spotify track, album, or playlist link.

For example:

```
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
```

The bot replies with the information Spotify makes available and a link to open the item on Spotify. Open that link to listen in Spotify.

---

## Configuration

For a complete list of settings, see [`.env.example`](.env.example). The most useful settings for a new installation are:

| Setting | What it does | Default |
| --- | --- | --- |
| `BOT_TOKEN` | Telegram token from BotFather. Required. | — |
| `DEFAULT_LANGUAGE` | Bot message language: `en` or `fa`. | `en` fallback; sample file uses `fa` |
| `ENABLE_AUTHORIZED_AUDIO_DELIVERY` | Enables the optional spotDL audio workflow when set to `true`; requires the acknowledgement below. | `false` |
| `AUDIO_DELIVERY_PERMISSIONS_ACK` | Required operator acknowledgement when audio delivery is enabled; it grants no permission. | `false` |
| `AUDIO_PROVIDERS` | Ordered spotDL providers used only by the optional audio path. | `soundcloud,youtube-music,youtube` |
| `DEFAULT_QUALITY` | Default audio bitrate for the optional workflow. | `320` |
| `MAX_DOWNLOAD_SIZE_MB` | Configured size ceiling; Telegram upload checks are capped at 49,000,000 bytes. | `50` |
| `DOWNLOAD_TIMEOUT_SECONDS` | Timeout for a spotDL download attempt. | `900` |
| `UPLOAD_TIMEOUT_SECONDS` | Timeout for one Telegram audio upload attempt. | `180` |
| `UPLOAD_RETRIES` | Maximum Telegram upload attempts. | `3` |
| `MAX_CONCURRENT_DOWNLOADS` | Maximum concurrent audio workers. | `3` |
| `SPOTDL_EXECUTABLE` | Optional explicit spotDL path; otherwise the active venv and then `PATH` are checked. | automatic |
| `RATE_LIMIT_REQUESTS` | Number of messages allowed in the rate-limit window. | `20` |
| `RATE_LIMIT_WINDOW_SECONDS` | Length of the rate-limit window in seconds. | `60` |
| `LOG_LEVEL` | Logging detail: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. | `INFO` |

The application reads `.env` automatically at startup. After changing a setting, stop and start the bot again.

### About audio delivery

The optional audio-delivery workflow is present in the code but disabled by default. It resolves audio through the configured spotDL providers; it does not fetch an audio file from Spotify itself. Enable it only when written platform permissions and rights-holder licences cover the exact workflow. Both `ENABLE_AUTHORIZED_AUDIO_DELIVERY=true` and `AUDIO_DELIVERY_PERMISSIONS_ACK=true` are required. The acknowledgement does not grant permission. Provider matching and delivery are best-effort, not guaranteed. See [docs/COMPLIANCE.md](docs/COMPLIANCE.md) and [docs/AUDIO_DELIVERY.md](docs/AUDIO_DELIVERY.md).

---

## Run the bot on an Ubuntu VPS

For a server that should keep running after you close your SSH session, use the supplied systemd installer:

- Recommended: Ubuntu 24.04.
- Ubuntu 22.04 needs a separately installed Python 3.11–3.15 runtime selected with `PYTHON_BIN`.
- The installer creates a dedicated `spotifybot` user and a `spotify-bot` systemd service.
- It asks for the Telegram token on a first-time install and preserves an existing `.env` during upgrades.

Read [the VPS and setup guide](docs/SETUP_INSTRUCTIONS.md) before running the installer. It installs the required Ubuntu packages but does not run a system-wide `apt-get upgrade`.

The repository does not currently provide an official Docker image or Docker Compose deployment.

---

## Troubleshooting

### `BOT_TOKEN is required` or Telegram rejects the token

- Check that `.env` is in the same folder as `bot.py`.
- Make sure the variable is named exactly `BOT_TOKEN`.
- Copy the full token from BotFather without spaces.
- If the token was exposed publicly, revoke it with BotFather and create a new one.

### `No module named 'telebot'` (or another missing module)

Activate the virtual environment and install the requirements again:

```bash
python -m pip install -r requirements.txt
```

### Python version is unsupported

Use Python 3.11–3.15. Check the active interpreter with:

```bash
python --version
```

If you created `venv` with the wrong interpreter, remove that `venv` folder and recreate it with a supported Python version.

### The bot starts but does not show a title or creator

The preview uses Spotify's oEmbed endpoint on a best-effort basis. Some links may not return preview metadata. The bot can still show the Spotify link; it does not use an HTML-scraping fallback.

### The bot says the message limit was reached

The built-in rate limiter is working. Wait for the time shown in the bot's reply before sending another link.

### Two bot processes are running

Only one polling process should use a bot token at a time. Stop duplicate local or server processes if Telegram reports a polling conflict.

---

## Project structure

```text
.
├── bot.py
├── config.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── start_bot.sh
├── setup_vps.sh
├── handlers/
│   ├── command_handler.py
│   ├── spotify_handler.py
│   └── callback_handler.py
├── utils/
├── scripts/
├── systemd/
├── tests/
└── docs/
    ├── README.fa.md
    ├── SETUP_INSTRUCTIONS.md
    └── COMPLIANCE.md
```

## For contributors

To install the test dependencies and run the test suite:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

The CI workflow also compiles the Python sources and checks the shell scripts on Python 3.11–3.15.

## Support and license

- Report a bug: [GitHub Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- License: [MIT](LICENSE)
- Project page: [matinshahabadi.ir](https://matinshahabadi.ir/projects/telegram-music-downloader-bot/)

---

**Project maintainer:** [Matin Shahabadi](https://github.com/power0matin)
