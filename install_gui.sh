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
    python3-setuptools \
    build-essential \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
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
echo "Step 2: Checking Python version..."
python3 --version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"
if [ "$(echo "$PYTHON_VERSION < 3.8" | bc 2>/dev/null)" = "1" ] || [ -z "$PYTHON_VERSION" ]; then
    echo "⚠ Warning: PyQt6 requires Python 3.8+"
    echo "Your Python version may be too old"
fi

echo ""
echo "Step 3: Upgrading pip and installing cffi..."
pip install --upgrade pip setuptools wheel
pip install cffi

echo ""
echo "Step 4: Installing PyQt6..."
echo "Attempting to install PyQt6 (this may take 10-20 minutes on Pi)..."
echo ""

# Try installing PyQt6 - first try with wheels, then force build from source
echo "Attempting installation methods..."
if pip install PyQt6 2>&1 | tee /tmp/pyqt6_install.log; then
    echo ""
    echo "✓ PyQt6 installed successfully!"
elif pip install --no-binary :all: PyQt6 2>&1 | tee -a /tmp/pyqt6_install.log; then
    echo ""
    echo "✓ PyQt6 installed successfully (built from source)!"
else
    echo ""
    echo "⚠ PyQt6 installation failed"
    echo ""
    echo "PyQt6 may not be compatible with your Python version or architecture"
    echo ""
    echo "Alternative solution: Use PyQt5 instead (much easier on Raspberry Pi)"
    echo "  Run: ./install_pyqt5.sh"
    echo "  Then we'll need to modify the GUI code to use PyQt5"
    echo ""
    echo "Or check your Python version:"
    echo "  python3 --version  # PyQt6 requires Python 3.8+"
    echo "  ./check_python.sh  # Detailed environment check"
    exit 1
fi

echo ""
echo "You can now run the GUI:"
echo "  ./flashd.py gui"

echo ""
echo "=== GUI Installation Complete ==="
echo "Run: ./flashd.py gui"

