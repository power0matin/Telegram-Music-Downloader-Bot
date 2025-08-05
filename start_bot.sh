#!/bin/bash

# Spotify Downloader Bot Startup Script

# Change to the script's directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable is not set."
    echo "Please set it using: export BOT_TOKEN='your_bot_token_here'"
    echo "Or create a .env file with BOT_TOKEN=your_bot_token_here"
    exit 1
fi

echo "🤖 Starting Spotify Downloader Bot..."
echo "Press Ctrl+C to stop the bot"

# Run the bot
python3 bot.py