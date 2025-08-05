#!/bin/bash

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

if [ -z "$BOT_TOKEN" ]; then
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable is not set."
    echo "Please set it using: export BOT_TOKEN='your_bot_token_here'"
    echo "Or create a .env file with BOT_TOKEN=your_bot_token_here"
    exit 1
fi

echo "🤖 Starting Spotify Downloader Bot..."
echo "Press Ctrl+C to stop the bot"

python3 bot.py
