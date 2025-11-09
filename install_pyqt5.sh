#!/bin/bash
# install_pyqt5.sh
# Alternative: Install PyQt5 instead of PyQt6 (easier on Raspberry Pi)

set -e

echo "=== Installing PyQt5 (Alternative to PyQt6) ==="
echo ""
echo "Note: This requires modifying the GUI code to use PyQt5 instead of PyQt6"
echo "PyQt5 is much easier to install on Raspberry Pi"
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

echo "Installing PyQt5 via apt (much faster than PyQt6)..."
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtsvg

echo ""
echo "✓ PyQt5 installed successfully!"
echo ""
echo "⚠ IMPORTANT: The GUI code needs to be modified to use PyQt5 instead of PyQt6"
echo "This is a code change that needs to be made in gui/main_window.py"
echo ""

