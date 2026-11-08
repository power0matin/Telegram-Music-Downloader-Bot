#!/bin/bash
set -euo pipefail

# ============================================================
# Telegram Spotify Downloader Bot - VPS Setup Script (Ubuntu)
# ============================================================
# This script installs all dependencies and runs the bot
# on Ubuntu 24.04, or Ubuntu 22.04 with Python 3.11-3.14 installed.
# Override the interpreter with: sudo PYTHON_BIN=python3.11 ./setup_vps.sh
#
# Usage:
#   chmod +x setup_vps.sh
#   sudo ./setup_vps.sh
#
# After setup, the bot runs as a systemd service that
# auto-starts on boot and restarts on crash.
# ============================================================

BOT_USER="spotifybot"
BOT_DIR="/opt/Telegram-Music-Downloader-Bot"
BOT_RUNTIME_DIR="${BOT_DIR}/runtime"
REPO_URL="https://github.com/power0matin/Telegram-Music-Downloader-Bot.git"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ---- Check root ----
if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo ./setup_vps.sh"
fi

# ---- Get BOT_TOKEN for a first-time install ----
echo ""
echo "==========================================="
echo "  Telegram Spotify Downloader Bot Setup"
echo "==========================================="
echo ""
PRESERVE_ENV=false
BOT_TOKEN=""
if [ -f "$BOT_DIR/.env" ] && grep -Eq '^BOT_TOKEN=.+$' "$BOT_DIR/.env"; then
    PRESERVE_ENV=true
    info "Existing .env detected; preserving its token and custom settings."
else
    read -r -s -p "Enter your Telegram BOT_TOKEN: " BOT_TOKEN
    echo ""
    if [ -z "$BOT_TOKEN" ]; then
        error "BOT_TOKEN cannot be empty!"
    fi
fi

# ---- System update & dependencies ----
info "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

info "Installing system dependencies..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl

# Verify installations
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    error "Python interpreter '$PYTHON_BIN' was not found. Set PYTHON_BIN to an installed Python 3.11-3.14 executable."
fi
"$PYTHON_BIN" --version || error "Selected Python interpreter could not be executed."
if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 15) else 1)'; then
    error "Python 3.11-3.14 is required by spotDL 4.6.x. Ubuntu 24.04 provides Python 3.12; on Ubuntu 22.04 install Python 3.11-3.14 and rerun with PYTHON_BIN=python3.11."
fi
PYTHON_MINOR="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHON_VENV_PACKAGE="python${PYTHON_MINOR}-venv"
if apt-cache show "$PYTHON_VENV_PACKAGE" >/dev/null 2>&1; then
    apt-get install -y -qq "$PYTHON_VENV_PACKAGE"
fi
ffmpeg -version >/dev/null 2>&1 || error "FFmpeg installation failed"
git --version || error "Git installation failed"

info "System dependencies installed."

# ---- Create bot user ----
if ! id "$BOT_USER" &>/dev/null; then
    info "Creating user: $BOT_USER"
    useradd -r -m -s /bin/bash "$BOT_USER"
else
    info "User $BOT_USER already exists."
fi

# ---- Clone or update repo ----
if [ -d "$BOT_DIR" ]; then
    info "Repository already exists at $BOT_DIR, pulling latest..."
    cd "$BOT_DIR"
    git -c safe.directory="$BOT_DIR" pull --ff-only origin main
else
    info "Cloning repository..."
    git clone "$REPO_URL" "$BOT_DIR"
    cd "$BOT_DIR"
fi

# ---- Setup virtual environment ----
info "Setting up Python virtual environment..."
if [ -x "venv/bin/python" ] && ! venv/bin/python -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 15) else 1)'; then
    warn "Existing virtual environment uses an unsupported Python version; recreating it."
    rm -rf venv
fi
if [ ! -x "venv/bin/python" ]; then
    "$PYTHON_BIN" -m venv venv
fi

source venv/bin/activate

# ---- Install Python dependencies ----
info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

spotdl --version || error "spotDL installation failed"

# ---- Runtime directories ----
mkdir -p downloads queue logs "$BOT_RUNTIME_DIR"

# spotDL 4.6.0 recommends a JavaScript runtime for yt-dlp. Install its local
# Deno binary into the same HOME that the systemd service will use. This is a
# best-effort optimization; SoundCloud and some YouTube downloads can still
# work without it.
if ! command -v deno >/dev/null 2>&1 \
    && [ ! -x "$BOT_RUNTIME_DIR/.config/spotdl/deno" ] \
    && [ ! -x "$BOT_RUNTIME_DIR/.spotdl/deno" ]; then
    info "Installing spotDL Deno runtime..."
    if HOME="$BOT_RUNTIME_DIR" "$BOT_DIR/venv/bin/spotdl" --download-deno; then
        info "Deno runtime installed."
    else
        warn "Deno installation failed; YouTube fallback reliability may be reduced."
    fi
fi

# ---- Create .env file without destroying update-time custom settings ----
if [ "$PRESERVE_ENV" = true ]; then
    info "Keeping existing .env configuration."
else
    info "Creating .env configuration..."
    cat > .env << EOF
BOT_TOKEN=${BOT_TOKEN}
DOWNLOAD_DIR=${BOT_DIR}/downloads
QUEUE_PATH=${BOT_DIR}/queue/queue.json
DEFAULT_QUALITY=320
MAX_DOWNLOAD_SIZE_MB=50
DOWNLOAD_TIMEOUT_SECONDS=900
UPLOAD_TIMEOUT_SECONDS=180
UPLOAD_RETRIES=3
MAX_CONCURRENT_DOWNLOADS=3
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=en
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
AUDIO_PROVIDERS=soundcloud,youtube-music,youtube
EOF
fi
chmod 600 .env

# ---- Create directories ----
chmod 755 downloads queue logs "$BOT_RUNTIME_DIR"

# ---- Set ownership ----
chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"

# ---- Create systemd service ----
info "Creating systemd service..."
cat > /etc/systemd/system/spotify-bot.service << EOF
[Unit]
Description=Telegram Spotify Downloader Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${BOT_USER}
Group=${BOT_USER}
WorkingDirectory=${BOT_DIR}
ExecStart=${BOT_DIR}/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=${BOT_DIR}/downloads ${BOT_DIR}/queue ${BOT_DIR}/logs ${BOT_RUNTIME_DIR}

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=HOME=${BOT_RUNTIME_DIR}

[Install]
WantedBy=multi-user.target
EOF

# ---- Enable and start service ----
info "Enabling and starting the bot service..."
systemctl daemon-reload
systemctl enable spotify-bot.service
systemctl restart spotify-bot.service

# ---- Verify ----
sleep 2
if systemctl is-active --quiet spotify-bot.service; then
    info "Bot is running successfully!"
else
    warn "Bot may not have started. Check logs with:"
    warn "  journalctl -u spotify-bot -f"
fi

# ---- Print summary ----
echo ""
echo "==========================================="
echo "  Setup Complete!"
echo "==========================================="
echo ""
echo "  Bot directory:  $BOT_DIR"
echo "  Bot user:       $BOT_USER"
echo "  Python venv:    $BOT_DIR/venv"
echo ""
echo "  Service commands:"
echo "    Start:    systemctl start spotify-bot"
echo "    Stop:     systemctl stop spotify-bot"
echo "    Restart:  systemctl restart spotify-bot"
echo "    Status:   systemctl status spotify-bot"
echo "    Logs:     journalctl -u spotify-bot -f"
echo ""
echo "  To update the bot:"
echo "    cd $BOT_DIR"
echo "    sudo -u $BOT_USER venv/bin/pip install -r requirements.txt"
echo "    sudo systemctl restart spotify-bot"
echo ""
echo "==========================================="
