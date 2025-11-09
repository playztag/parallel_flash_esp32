#!/bin/bash
# install_gui.sh
# Install GUI dependencies (PyQt6) on Raspberry Pi

set -e

echo "=== Installing GUI Dependencies (PyQt6) ==="
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run setup_pi.sh first."
        exit 1
    fi
fi

# Install system dependencies for PyQt6
echo "Step 1: Installing system dependencies..."
echo "This may take a few minutes..."
sudo apt update
sudo apt install -y \
    python3-dev \
    build-essential \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    qt6-base-dev \
    libqt6gui6 \
    libqt6widgets6

echo ""
echo "Step 2: Installing PyQt6 via pip..."
echo "This may take 10-20 minutes on Raspberry Pi (compiling from source)..."
echo ""

# Try installing PyQt6
if pip install PyQt6; then
    echo ""
    echo "✓ PyQt6 installed successfully!"
    echo ""
    echo "You can now run the GUI:"
    echo "  ./flashd.py gui"
else
    echo ""
    echo "⚠ PyQt6 installation failed"
    echo ""
    echo "Troubleshooting options:"
    echo "1. Check if you have enough disk space: df -h"
    echo "2. Increase swap space if Pi runs out of memory"
    echo "3. Try installing with verbose output: pip install --verbose PyQt6"
    echo "4. Check INSTALL_PYQT6.md for more troubleshooting tips"
    exit 1
fi

echo ""
echo "=== GUI Installation Complete ==="
echo "Run: ./flashd.py gui"

