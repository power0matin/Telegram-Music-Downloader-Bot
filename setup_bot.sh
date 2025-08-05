#!/bin/bash

# =====================================
# 🎵 Spotify Downloader Bot Setup
# =====================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}🎵 $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Welcome message
clear
echo -e "${CYAN}"
cat << "EOF"
   _____ ____   ____  _______ _____ ________     __
  / ____/ __ \ / __ \|__   __|_   _|  ____\ \   / /
 | (___| |  | | |  | |  | |    | | | |__   \ \_/ / 
  \___ \ |  | | |  | |  | |    | | |  __|   \   /  
  ____) | |__| | |__| |  | |   _| |_| |       | |   
 |_____/ \____/ \____/   |_|  |_____|_|       |_|   
                                                    
          DOWNLOADER BOT SETUP SCRIPT
EOF
echo -e "${NC}"

print_header "Starting Automatic Setup"

# Change to script directory
cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)

print_status "Working directory: $SCRIPT_DIR"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. This is not recommended for security reasons."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled by user"
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_header "Checking Prerequisites"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
    
    # Check if Python version is >= 3.8
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        print_success "Python version is compatible (>= 3.8)"
    else
        print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 is not installed!"
    print_status "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-venv python3-pip"
    echo "  macOS:         brew install python3"
    exit 1
fi

# Check Git
if command_exists git; then
    print_success "Git is available"
else
    print_warning "Git not found. Installing Git..."
    if command_exists apt; then
        sudo apt update && sudo apt install -y git
    elif command_exists yum; then
        sudo yum install -y git
    elif command_exists brew; then
        brew install git
    else
        print_error "Could not install Git automatically. Please install it manually."
        exit 1
    fi
fi

# Check and install system dependencies
print_header "Installing System Dependencies"

if command_exists apt; then
    print_status "Detected Debian/Ubuntu system"
    print_status "Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3-venv python3-pip ffmpeg curl wget
    print_success "System dependencies installed"
elif command_exists yum; then
    print_status "Detected CentOS/RHEL system"
    print_status "Installing system dependencies..."
    sudo yum install -y python3-venv python3-pip ffmpeg curl wget
    print_success "System dependencies installed"
elif command_exists brew; then
    print_status "Detected macOS system"
    print_status "Installing system dependencies..."
    brew install ffmpeg
    print_success "System dependencies installed"
else
    print_warning "Could not detect package manager. Please install ffmpeg manually."
fi

# Create virtual environment
print_header "Setting Up Python Environment"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing virtual environment..."
        rm -rf venv
    else
        print_status "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Verify installation
print_header "Verifying Installation"

print_status "Testing imports..."
python3 -c "
import sys
print('✓ Python version:', sys.version)
try:
    import telebot
    print('✓ pyTelegramBotAPI imported successfully')
except ImportError as e:
    print('✗ Failed to import pyTelegramBotAPI:', e)
    sys.exit(1)

try:
    import requests
    print('✓ requests imported successfully')
except ImportError as e:
    print('✗ Failed to import requests:', e)
    sys.exit(1)

try:
    import spotdl
    print('✓ spotdl imported successfully')
except ImportError as e:
    print('✗ Failed to import spotdl:', e)
    sys.exit(1)

print('✓ All dependencies verified')
"

if [ $? -eq 0 ]; then
    print_success "All dependencies verified successfully"
else
    print_error "Dependency verification failed"
    exit 1
fi

# Check if bot files exist
print_status "Checking bot files..."
required_files=("bot.py" "config.py" "handlers/spotify_handler.py" "handlers/callback_handler.py" "utils/downloader.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file found"
    else
        print_error "✗ $file missing"
        exit 1
    fi
done

# Make scripts executable
print_status "Making scripts executable..."
chmod +x start_bot.sh 2>/dev/null || true
chmod +x setup_bot.sh 2>/dev/null || true

# Create .env file template
print_header "Bot Configuration"

if [ ! -f ".env" ]; then
    print_status "Creating .env file template..."
    cat > .env << 'EOF'
# Telegram Bot Token
# Get your token from @BotFather on Telegram
BOT_TOKEN=your_bot_token_here

# Optional: Download quality (128 or 320)
DEFAULT_QUALITY=320

# Optional: Maximum retries for downloads
MAX_RETRIES=5
EOF
    print_success ".env file created"
else
    print_warning ".env file already exists"
fi

# Bot token setup
print_header "Telegram Bot Token Setup"

if [ -f ".env" ] && grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    print_warning "Bot token not configured yet"
    echo
    echo -e "${YELLOW}To get your Telegram Bot Token:${NC}"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot and follow the instructions"
    echo "3. Copy your bot token"
    echo
    read -p "Do you want to enter your bot token now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your bot token: " BOT_TOKEN
        if [ ! -z "$BOT_TOKEN" ]; then
            sed -i "s/BOT_TOKEN=your_bot_token_here/BOT_TOKEN=$BOT_TOKEN/" .env
            print_success "Bot token configured"
        fi
    fi
fi

# Final setup
print_header "Final Setup"

# Create directories
mkdir -p queue downloads logs
print_success "Required directories created"

# Setup complete
print_header "Setup Complete!"

echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SETUP SUCCESSFUL! 🎉                   ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Your Spotify Downloader Bot is ready to use!${NC}"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure your bot token in .env file (if not done already)"
echo "2. Run the bot: ./start_bot.sh"
echo
echo -e "${YELLOW}Quick Commands:${NC}"
echo "  Start bot:    ./start_bot.sh"
echo "  Stop bot:     Ctrl+C"
echo "  View logs:    tail -f logs/bot.log"
echo
echo -e "${YELLOW}Configuration Files:${NC}"
echo "  Bot config:   .env"
echo "  Dependencies: requirements.txt"
echo "  Documentation: README.md"
echo
echo -e "${YELLOW}Troubleshooting:${NC}"
echo "  If you encounter issues, check:"
echo "  - Bot token is correctly set in .env"
echo "  - Internet connection is working"
echo "  - Spotify URLs are valid"
echo
echo -e "${GREEN}Happy downloading! 🎵${NC}"
echo
echo -e "${BLUE}For support: Check README.md or open an issue on GitHub${NC}"