#!/bin/bash
set -e

# ============================================================
# Telegram Spotify Downloader Bot - VPS Setup Script (Ubuntu)
# ============================================================
# This script installs all dependencies and runs the bot
# on a fresh Ubuntu VPS (20.04/22.04/24.04).
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
REPO_URL="https://github.com/power0matin/Telegram-Music-Downloader-Bot.git"

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

# ---- Get BOT_TOKEN from user ----
echo ""
echo "==========================================="
echo "  Telegram Spotify Downloader Bot Setup"
echo "==========================================="
echo ""
read -p "Enter your Telegram BOT_TOKEN: " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    error "BOT_TOKEN cannot be empty!"
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
python3 --version || error "Python3 installation failed"
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
    git pull origin main
else
    info "Cloning repository..."
    git clone "$REPO_URL" "$BOT_DIR"
    cd "$BOT_DIR"
fi

# ---- Setup virtual environment ----
info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# ---- Install Python dependencies ----
info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Install spotdl (the actual download engine)
info "Installing spotdl..."
pip install spotdl -q

# ---- Create .env file ----
info "Creating .env configuration..."
cat > .env << EOF
BOT_TOKEN=${BOT_TOKEN}
DOWNLOAD_DIR=${BOT_DIR}/downloads
QUEUE_PATH=${BOT_DIR}/queue/queue.json
DEFAULT_QUALITY=320
MAX_DOWNLOAD_SIZE_MB=50
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=en
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
EOF

# ---- Create directories ----
mkdir -p downloads queue logs
chmod 755 downloads queue logs

# ---- Set ownership ----
chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"

# ---- Create systemd service ----
info "Creating systemd service..."
cat > /etc/systemd/system/spotify-bot.service << EOF
[Unit]
Description=Telegram Spotify Downloader Bot
After=network.target
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
ReadWritePaths=${BOT_DIR}/downloads ${BOT_DIR}/queue ${BOT_DIR}/logs

# Environment
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# ---- Enable and start service ----
info "Enabling and starting the bot service..."
systemctl daemon-reload
systemctl enable spotify-bot.service
systemctl start spotify-bot.service

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
