#!/bin/bash
# setup_pi.sh
# Quick setup script for Raspberry Pi

set -e

echo "=== Parallel ESP32 Flasher - Pi Setup ==="
echo ""

# Check if we're on a Pi (optional check)
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi, but continuing anyway..."
fi

# Install system dependencies
echo "Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv
# Note: PyQt6 is installed via pip, not apt (not available in Pi repos)

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate venv and install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Try to install GUI dependencies (optional - can skip if it fails)
echo ""
echo "Attempting to install GUI dependencies (PyQt6)..."
echo "Note: This may take a while on Raspberry Pi and can be skipped if you only need CLI mode"
if pip install PyQt6 2>&1 | tee /tmp/pyqt6_install.log; then
    echo "✓ PyQt6 installed successfully - GUI mode available"
else
    echo "⚠ PyQt6 installation failed - GUI mode will not be available"
    echo "  CLI mode will still work fine"
    echo "  To retry later, install system dependencies first:"
    echo "    sudo apt install -y python3-dev build-essential libgl1-mesa-dev libgles2-mesa-dev libxkbcommon-x11-0"
    echo "    Then: pip install PyQt6"
fi

# Make flashd.py executable
chmod +x flashd.py

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To use:"
echo "  source venv/bin/activate"
echo "  ./flashd.py list    # List devices"
echo "  ./flashd.py flash   # Flash all devices"
echo "  ./flashd.py gui     # Launch GUI"
echo ""

