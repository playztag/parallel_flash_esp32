#!/bin/bash
# deploy_to_pi.sh
# Script to deploy parallel_flash_esp32 to Raspberry Pi

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Parallel ESP32 Flasher - Raspberry Pi Deployment ===${NC}\n"

# Get Pi IP address
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <pi_ip_address>${NC}"
    echo -e "${YELLOW}Example: $0 192.168.1.100${NC}"
    echo ""
    echo "Finding Raspberry Pi on network..."
    
    # Try common Pi hostnames
    for hostname in raspberrypi raspberrypi.local rpi; do
        if ping -c 1 -W 1 "$hostname" &>/dev/null; then
            PI_IP=$(getent hosts "$hostname" | awk '{print $1}')
            echo -e "${GREEN}Found Pi at: $PI_IP ($hostname)${NC}"
            read -p "Use this IP? (y/n): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                break
            fi
        fi
    done
    
    if [ -z "$PI_IP" ]; then
        echo -e "${RED}Could not auto-detect Pi. Please provide IP address:${NC}"
        read -p "Pi IP address: " PI_IP
    fi
else
    PI_IP="$1"
fi

echo -e "\n${GREEN}Target Pi: $PI_IP${NC}"

# Check SSH access
echo -e "\n${YELLOW}Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "pi@$PI_IP" exit 2>/dev/null; then
    echo -e "${YELLOW}SSH key not set up. You'll be prompted for password.${NC}"
    echo -e "${YELLOW}To avoid password prompts, set up SSH keys:${NC}"
    echo -e "  ssh-copy-id pi@$PI_IP"
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME=$(basename "$PROJECT_DIR")

echo -e "\n${GREEN}Copying project to Pi...${NC}"
echo "Source: $PROJECT_DIR"
echo "Destination: pi@$PI_IP:~/parallel_flash_esp32"

# Create remote directory and copy files
ssh "pi@$PI_IP" "mkdir -p ~/parallel_flash_esp32" || true

# Use rsync if available, otherwise use scp
if command -v rsync &> /dev/null; then
    echo -e "${YELLOW}Using rsync (faster, excludes venv and __pycache__)...${NC}"
    rsync -avz --progress \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude 'static/logs/*' \
        --exclude 'static/flash_history.db' \
        "$PROJECT_DIR/" "pi@$PI_IP:~/parallel_flash_esp32/"
else
    echo -e "${YELLOW}Using scp (slower)...${NC}"
    scp -r "$PROJECT_DIR"/* "pi@$PI_IP:~/parallel_flash_esp32/"
fi

echo -e "\n${GREEN}Setting up environment on Pi...${NC}"
ssh "pi@$PI_IP" << 'ENDSSH'
cd ~/parallel_flash_esp32

# Install system dependencies
echo "Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-pyqt6 || true

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make flashd.py executable
chmod +x flashd.py

echo "Setup complete!"
ENDSSH

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "\n${YELLOW}To run on Pi:${NC}"
echo "  ssh pi@$PI_IP"
echo "  cd ~/parallel_flash_esp32"
echo "  source venv/bin/activate"
echo "  ./flashd.py list    # List connected devices"
echo "  ./flashd.py flash   # Flash all devices"
echo "  ./flashd.py gui     # Launch GUI"
echo ""
echo -e "${YELLOW}Or run remotely:${NC}"
echo "  ssh pi@$PI_IP 'cd ~/parallel_flash_esp32 && source venv/bin/activate && ./flashd.py list'"

