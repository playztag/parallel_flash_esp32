# Quick Start for Raspberry Pi

## One-Time Setup on Pi

SSH into your Pi or open terminal via VNC:

```bash
# Clone the repository
cd ~
git clone git@github.com:playztag/parallel_flash_esp32.git
cd parallel_flash_esp32

# Run automated setup
chmod +x setup_pi.sh
./setup_pi.sh
```

## Running the Tool

### GUI Mode (via VNC - Recommended!)
```bash
cd ~/parallel_flash_esp32
source venv/bin/activate
./flashd.py gui
```
The GUI will appear on the Pi's desktop - you'll see it in your VNC window!

### CLI Mode
```bash
cd ~/parallel_flash_esp32
source venv/bin/activate

# List connected ESP32 devices
./flashd.py list

# Flash all devices
./flashd.py flash

# Flash specific device
./flashd.py flash --port /dev/ttyUSB0

# Use custom firmware
./flashd.py flash --firmware firmware.bin
```

## Updating

When you push changes to GitHub:

```bash
cd ~/parallel_flash_esp32
git pull
source venv/bin/activate
pip install -r requirements.txt  # In case requirements changed
```

## Copying Firmware

If you have a firmware binary to flash:

```bash
# Copy firmware to Pi
scp firmware.bin pi@192.168.54.181:~/parallel_flash_esp32/

# Or via VNC file transfer
```

Then flash it:
```bash
./flashd.py flash --firmware firmware.bin
```

