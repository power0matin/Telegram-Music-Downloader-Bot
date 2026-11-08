# Installation and deployment guide

This guide explains how to run the bot on your own computer and how to keep it running on an Ubuntu VPS.

> **What this project currently does:** by default, it previews limited Spotify information and provides a link to Spotify. It does not download or send audio files. Read [COMPLIANCE.md](COMPLIANCE.md) before changing the optional audio-delivery setting.

For a shorter overview, see the [main README](../README.md). The [Persian guide](README.fa.md) is also available.

---

## 1. What you need

For a local installation:

- Python **3.11–3.14**
- Git
- Internet access
- A Telegram account

You do not need FFmpeg for the default preview-only mode. FFmpeg is used only by the optional audio-processing path.

For a VPS installation, use Ubuntu 24.04 where possible. Ubuntu 22.04 needs a separately installed compatible Python runtime; details are in the VPS section below.

## 2. Create a Telegram bot

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather).
2. Send `/newbot`.
3. Follow the prompts to choose a display name and username.
4. Copy the bot token.

Keep the token private. Anyone who gets it can control your bot. If it is exposed, revoke it with BotFather and generate a new one.

## 3. Download the project

Open a terminal and run:

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
```

## 4. Install Python dependencies

Create a virtual environment before installing packages. This avoids changing your system-wide Python installation.

### Linux / macOS

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

List the Python versions available on your computer:

```powershell
py -0p
```

Choose one installed version between 3.11 and 3.14. The example uses 3.12; change it if your installed version is different.

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows Command Prompt (CMD)

```cmd
py -3.12 -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell does not allow script activation, use Command Prompt or review your local PowerShell execution policy. Do not change the machine-wide policy just to activate this project.

After activation, the terminal usually shows `(venv)`. Keep this environment active while installing packages and running the bot.

## 5. Configure the bot

Copy the example configuration to a new `.env` file in the project root.

**Linux / macOS:**

```bash
cp .env.example .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

Open `.env` in a text editor. Set at least the following values:

```dotenv
BOT_TOKEN=your_real_token_from_BotFather
DEFAULT_LANGUAGE=fa
ENABLE_AUTHORIZED_AUDIO_DELIVERY=false
```

- Replace the example value of `BOT_TOKEN` with your real token.
- Use `fa` for Persian messages or `en` for English messages.
- Leave `ENABLE_AUTHORIZED_AUDIO_DELIVERY=false` for ordinary use.

The application loads `.env` automatically; you do not need to run `export` when you use this file. The repository's `.gitignore` excludes `.env`, but still do not share it or commit it.

## 6. Start and test the bot

With the virtual environment activated, run:

```bash
python bot.py
```

The bot contacts Telegram during startup to validate the token. Keep the terminal open while the bot is running. Press `Ctrl+C` to stop it.

On Linux/macOS, you can alternatively run the helper script:

```bash
chmod +x start_bot.sh
./start_bot.sh
```

The helper expects a virtual environment named `venv`. On Windows, run `python bot.py` directly.

To test the bot:

1. Open your bot in Telegram.
2. Send `/start`.
3. Send `/help`.
4. Send a public Spotify track, album, or playlist URL.

The bot displays the limited information returned by Spotify's oEmbed service, when available, and provides the Spotify link. If Spotify does not return preview metadata, the link can still be shown.

---

## 7. Configuration reference

The complete example is in [`.env.example`](../.env.example). Common settings:

| Setting | Description | Default |
| --- | --- | --- |
| `BOT_TOKEN` | Required Telegram bot token. | — |
| `DEFAULT_LANGUAGE` | Bot message language: `en` or `fa`. | `en` in code; `fa` in the sample file |
| `ENABLE_AUTHORIZED_AUDIO_DELIVERY` | Gate for the optional audio-delivery path. Keep disabled unless all required permissions and licences are in place. | `false` |
| `RATE_LIMIT_REQUESTS` | Allowed requests within the rate-limit window. | `20` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate-limit window length, in seconds. | `60` |
| `LOG_LEVEL` | Log detail: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. | `INFO` |

Other settings in `.env.example` are mainly for the optional audio-delivery path or advanced deployments. Change them only when you understand their effect. Restart the bot after editing `.env`.

### Audio-delivery setting

Do not set `ENABLE_AUTHORIZED_AUDIO_DELIVERY=true` just to try to download songs from Spotify links. This setting is only a technical gate; it does not grant Spotify, provider, or copyright permissions. The exact intended workflow must be covered by written platform permissions and rights-holder licences. Read [COMPLIANCE.md](COMPLIANCE.md) before making any change.

---

## 8. Install on an Ubuntu VPS

The repository includes `setup_vps.sh`, which installs the bot as a systemd service.

### Supported setup

- **Ubuntu 24.04:** recommended; the installer uses the system Python 3.12.
- **Ubuntu 22.04:** install Python 3.11–3.14 separately, including its venv support, and select it with `PYTHON_BIN`.
- Other operating systems are not supported by this automated installer.

### Before running the installer

The script performs system package updates and an `apt-get upgrade`, installs system dependencies, creates a service user, downloads the repository into `/opt/Telegram-Music-Downloader-Bot`, creates a virtual environment, and configures systemd.

Run it on a server where you have reviewed and are comfortable applying Ubuntu package upgrades. On a production server, take a backup and schedule a maintenance window first.

### Ubuntu 24.04

Clone the repository and run the installer:

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
chmod +x setup_vps.sh
sudo ./setup_vps.sh
```

On a first-time installation, the script asks for your Telegram bot token without displaying it while you type. It then creates the configuration file and starts the service.

### Ubuntu 22.04

The system Python on Ubuntu 22.04 is too old for this project. Install a supported Python runtime (3.11–3.14) and its venv package first. Then run the installer with the exact interpreter name, for example:

```bash
sudo PYTHON_BIN=python3.11 ./setup_vps.sh
```

The selected interpreter must already be available on the server.

### Check the service

After installation:

```bash
sudo systemctl status spotify-bot
```

Follow the logs:

```bash
sudo journalctl -u spotify-bot -f
```

Useful service commands:

```bash
sudo systemctl restart spotify-bot
sudo systemctl stop spotify-bot
sudo systemctl start spotify-bot
sudo systemctl is-active spotify-bot
```

The installer creates a dedicated Linux user named `spotifybot`. The application files live in `/opt/Telegram-Music-Downloader-Bot`.

### Update an existing VPS installation

The installer preserves an existing `.env` when it finds a configured bot token. For a normal code update, connect to the server and run:

```bash
cd /opt/Telegram-Music-Downloader-Bot
sudo -u spotifybot git pull --ff-only origin main
sudo -u spotifybot venv/bin/pip install -r requirements.txt
sudo systemctl restart spotify-bot
sudo systemctl status spotify-bot
```

If you change `.env`, restart the service so the new values are loaded.

---

## 9. Troubleshooting

### The application says `BOT_TOKEN is required`

- Check that `.env` is in the same folder as `bot.py`.
- Confirm that the variable is named exactly `BOT_TOKEN`.
- Make sure you replaced the example token with the token from BotFather.

### Telegram reports an invalid token

Copy the complete token again. If it was exposed, revoke it through BotFather and use a new one.

### `No module named 'telebot'` or another missing package

Activate the project's virtual environment and run:

```bash
python -m pip install -r requirements.txt
```

Make sure `python` points to the virtual environment's interpreter:

```bash
python --version
```

### Unsupported Python version

Use Python 3.11–3.14. If the existing virtual environment was created with another version, remove the `venv` folder and recreate it with a supported interpreter.

### No preview title is shown

Spotify's oEmbed metadata is best-effort. Some links do not return preview information. The bot does not scrape the Spotify page as a fallback; it can still show the canonical Spotify URL.

### The bot does not respond

- Check that the process is still running.
- Check the token and internet connection.
- On a VPS, inspect `sudo journalctl -u spotify-bot -f`.
- Make sure another copy of the bot is not polling with the same token. Only one polling process should use a token at a time.

### Audio is not sent

This is expected in the default configuration. The bot is a Spotify link-preview bot by default, not an audio downloader. Do not enable audio delivery without the permissions described in [COMPLIANCE.md](COMPLIANCE.md).

---

## 10. Development and tests

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest -q
```

The CI workflow also compiles the Python sources and validates shell scripts on Python 3.11, 3.12, 3.13, and 3.14.

## Security reminders

- Never publish your Telegram bot token.
- Keep `.env` out of Git commits.
- Use a dedicated service user on a VPS.
- Keep audio delivery disabled unless the exact workflow has all required written permissions and licences.
- Do not bypass platform access controls or provider restrictions.

## Related files

- [Main README](../README.md)
- [Persian README](README.fa.md)
- [Changelog](../CHANGELOG.md)
- [Compliance notes](COMPLIANCE.md)
- [Example environment configuration](../.env.example)
- [VPS installer](../setup_vps.sh)
