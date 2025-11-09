# Quick Fix: Missing Dependencies

If you get "no module named yaml" or other import errors:

## On Your Pi:

```bash
cd ~/parallel_flash_esp32

# Make sure virtual environment is activated
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- esptool
- pyserial
- pyudev
- asyncio-mqtt
- pyyaml (this fixes the "yaml" error)

## If setup wasn't completed:

If you haven't run setup yet:

```bash
cd ~/parallel_flash_esp32
chmod +x setup_pi.sh
./setup_pi.sh
```

This will:
1. Install system packages
2. Create virtual environment
3. Install all Python dependencies

