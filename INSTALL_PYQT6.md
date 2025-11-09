# Installing PyQt6 on Raspberry Pi

PyQt6 can be difficult to install on Raspberry Pi. Here are several options:

## Option 1: Install System Dependencies First (Recommended)

PyQt6 needs system libraries to build. Install them first:

```bash
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
    libxkbcommon0

# Then install PyQt6
source venv/bin/activate
pip install PyQt6
```

## Option 2: Use Pre-built Wheel (Faster)

If available, use a pre-built wheel:

```bash
source venv/bin/activate
pip install --only-binary :all: PyQt6
```

## Option 3: Skip GUI (CLI Only)

The tool works perfectly fine without PyQt6! Just use CLI mode:

```bash
./flashd.py list    # List devices
./flashd.py flash    # Flash devices
```

GUI mode (`./flashd.py gui`) requires PyQt6, but all other features work without it.

## Option 4: Use PyQt5 Instead (Easier on Pi)

If PyQt6 continues to fail, you could modify the code to use PyQt5, which is easier to install:

```bash
sudo apt install -y python3-pyqt5
```

However, this would require code changes to the GUI module.

## Troubleshooting

If installation fails with "error while generating package metadata":

1. **Check Python version**: PyQt6 requires Python 3.8+
   ```bash
   python3 --version
   ```

2. **Install build tools**:
   ```bash
   sudo apt install -y python3-dev build-essential
   ```

3. **Increase swap space** (if Pi runs out of memory during build):
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

4. **Try with more verbose output**:
   ```bash
   pip install --verbose PyQt6
   ```

## Current Status

- ✅ **CLI mode works without PyQt6** - All flashing features available
- ⚠️ **GUI mode requires PyQt6** - Optional feature

