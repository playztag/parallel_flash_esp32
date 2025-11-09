# How to Run the ESP32 Flasher

## Prerequisites

Make sure you've completed setup:
```bash
cd ~/parallel_flash_esp32
source venv/bin/activate
```

## CLI Mode (Works Without GUI)

### List Connected ESP32 Devices
```bash
./flashd.py list
```

### Flash All Connected Devices
```bash
./flashd.py flash
```

### Flash a Specific Device
```bash
./flashd.py flash --port /dev/ttyUSB0
```

### Flash with Custom Firmware
```bash
./flashd.py flash --firmware firmware.bin
```

### Monitor Mode (Auto-flash when device connects)
```bash
./flashd.py monitor
```

### View Statistics
```bash
./flashd.py stats
```

## GUI Mode (Requires PyQt6 or PyQt5)

### Check if GUI is Available
```bash
./flashd.py gui
```

If you get an error about PyQt6, you need to install it first (see below).

### Launch GUI
```bash
./flashd.py gui
```

The GUI will appear on your Pi's desktop. If you're using VNC, you'll see it in your VNC window.

## Quick Start Example

1. **Connect ESP32 devices** to your Pi via USB

2. **List devices:**
   ```bash
   cd ~/parallel_flash_esp32
   source venv/bin/activate
   ./flashd.py list
   ```

3. **Flash all devices:**
   ```bash
   ./flashd.py flash
   ```

4. **Or use GUI:**
   ```bash
   ./flashd.py gui
   ```

## Troubleshooting

### "No devices found"
- Make sure ESP32 is connected via USB
- Check permissions: `ls -la /dev/ttyUSB*`
- Add user to dialout group: `sudo usermod -a -G dialout $USER` (then logout/login)

### "GUI dependencies not available"
- Install PyQt6: `./install_gui.sh`
- Or use CLI mode (works without GUI)

### "Permission denied" on /dev/ttyUSB*
```bash
sudo usermod -a -G dialout $USER
# Logout and login again
```

