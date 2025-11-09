# Parallel ESP32 Flash Station

A parallel ESP32 firmware flashing and QA tool for Linux/Raspberry Pi with automatic device detection and GUI dashboard.

## Features

- **Parallel Flashing**: Flash multiple ESP32 devices simultaneously
- **Auto-Detection**: Automatic USB device hotplug detection
- **GUI Dashboard**: Real-time status display with progress tracking
- **CLI Support**: Full command-line interface for headless operation
- **Metrics & Logging**: SQLite database tracking with CSV export
- **Cross-Platform**: Works on Linux, macOS, and Raspberry Pi

## Architecture

```
┌─────────────────┐
│  PyQt6 GUI      │  Optional graphical interface
├─────────────────┤
│  Flash Daemon   │  Core flashing engine
├─────────────────┤
│  Device Manager │  USB hotplug detection (pyudev/polling)
├─────────────────┤
│  esptool.py     │  ESP32 flashing tool
└─────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- `esptool.py` (installed automatically via requirements)
- For GUI: PyQt6
- For Linux hotplug: pyudev (optional, falls back to polling)

### Setup

```bash
# Clone or navigate to project directory
cd parallel_flash_esp32

# Install dependencies
pip install -r requirements.txt

# Make daemon executable
chmod +x flashd.py
```

### Raspberry Pi Setup

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to customize settings:

```yaml
baud_rate: 921600          # Flash baud rate
chip: esp32                # Target chip type
flash_offset: 0x1000       # Flash memory offset
firmware_path: static/firmware/firmware.bin
verify: true               # Verify after flashing
max_workers: 10            # Max parallel operations
mqtt:
  enabled: false           # MQTT reporting (future)
  broker: localhost
  topic: zflash/results
```

## Usage

### GUI Mode

```bash
./flashd.py gui
```

**Features:**
- 🔄 Refresh Devices - Scan for connected ESP32 devices
- ⚡ Flash All - Flash all connected devices in parallel
- 🛑 Stop All - Cancel all ongoing operations
- 📁 Select Firmware - Choose firmware binary to flash
- 🔢 Reset Stats - Clear flash history statistics

Click any device card to flash it individually.

### CLI Mode

**List connected devices:**
```bash
./flashd.py list
```

**Flash all devices:**
```bash
./flashd.py flash
```

**Flash specific device:**
```bash
./flashd.py flash --port /dev/ttyUSB0
```

**Use custom firmware:**
```bash
./flashd.py flash --firmware /path/to/firmware.bin
```

**Monitor mode (auto-flash on connect):**
```bash
./flashd.py monitor
```

**View statistics:**
```bash
./flashd.py stats
```

## Directory Structure

```
parallel_flash_esp32/
├── flashd.py              # Main daemon entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── core/                  # Core modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── flasher.py         # esptool wrapper
│   ├── device_manager.py  # USB device detection
│   ├── logger.py          # Logging utilities
│   └── db.py              # SQLite database
├── gui/                   # PyQt6 GUI
│   ├── __init__.py
│   ├── main_window.py     # Main window
│   └── widgets/
│       ├── __init__.py
│       └── port_widget.py # Port status widget
└── static/
    ├── firmware/          # Firmware binaries
    ├── logs/              # Log files
    └── flash_history.db   # SQLite database
```

## Development

### Running Tests

```bash
# Test device detection
python -c "from core import DeviceManager; dm = DeviceManager(); print(dm.scan_devices())"

# Test flasher (dry run)
python -c "from core import ESP32Flasher; f = ESP32Flasher(); print(f.get_chip_info('/dev/ttyUSB0'))"
```

### Adding Custom Features

1. **Custom flash offsets**: Modify `core/flasher.py` to support multiple partition flashing
2. **MQTT reporting**: Enable in `config.yaml` and implement in `flashd.py`
3. **Web UI**: Add Flask REST API in new `api/` module
4. **QR code scanning**: Add barcode support to GUI

## Troubleshooting

### Permission Denied on Linux

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

### Device Not Detected

```bash
# Check USB devices
ls -la /dev/ttyUSB* /dev/ttyACM*

# Test with esptool directly
esptool.py --port /dev/ttyUSB0 chip_id
```

### GUI Won't Start

```bash
# Install PyQt6
pip install PyQt6

# For Raspberry Pi Desktop
sudo apt install python3-pyqt6
```

## Roadmap

- [x] v0.1 - CLI multi-port flasher
- [x] v0.2 - Auto-detect + async flashing
- [x] v0.3 - PyQt6 GUI dashboard
- [x] v0.4 - SQLite logging & metrics
- [ ] v0.5 - REST API for headless control
- [ ] v0.6 - MQTT integration
- [ ] v1.0 - Production release

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/parallel_flash_esp32/issues)
- Documentation: See this README

---

**Made for factory-grade ESP32 production flashing** ⚡
