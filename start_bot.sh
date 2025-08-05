#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable is not set."
    echo "Please set it using: export BOT_TOKEN='your_bot_token_here'"
    echo "Or create a .env file with BOT_TOKEN=your_bot_token_here"
    exit 1
fi

echo "🤖 Starting Spotify Downloader Bot..."
echo "Press Ctrl+C to stop the bot"

# Set PYTHONPATH and run the bot
PYTHONPATH=$(pwd) python3 bot.py