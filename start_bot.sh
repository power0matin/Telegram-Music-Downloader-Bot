#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ ! -x "venv/bin/python" ]; then
    echo "Virtual environment not found. Run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo "Starting Spotify Downloader Bot..."
echo "Press Ctrl+C to stop the bot"

# config.py loads .env safely through python-dotenv. Avoid shell-parsing .env;
# proxy URLs and other values may legitimately contain spaces or shell symbols.
exec venv/bin/python bot.py
