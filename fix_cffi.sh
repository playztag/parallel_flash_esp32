#!/bin/bash
# fix_cffi.sh
# Fix cffi build errors on Raspberry Pi

set -e

echo "=== Fixing cffi Build Error ==="
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

echo "Step 1: Installing build tools and dependencies..."
sudo apt update
sudo apt install -y \
    python3-dev \
    python3-setuptools \
    build-essential \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev

echo ""
echo "Step 2: Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 3: Installing cffi..."
if pip install cffi; then
    echo "✓ cffi installed successfully"
else
    echo "⚠ cffi installation failed"
    echo ""
    echo "Trying alternative method..."
    pip install --no-cache-dir cffi
fi

echo ""
echo "=== cffi Fix Complete ==="
echo "You can now try installing PyQt6 again:"
echo "  pip install PyQt6"

