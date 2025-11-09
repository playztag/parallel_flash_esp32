# Deployment Instructions for Raspberry Pi

## Your Pi Details
- IP Address: 192.168.54.181
- VNC: Available (great for GUI!)

## Option 1: Automated Deployment (Recommended)

Run this command and enter your Pi password when prompted:

```bash
cd /Users/quangan/Documents/Sandbox/parallel_flash_esp32
./deploy_to_pi.sh 192.168.54.181
```

This will:
1. Copy all project files to `~/parallel_flash_esp32` on the Pi
2. Install system packages (python3, pip, venv, PyQt6)
3. Create virtual environment
4. Install Python dependencies
5. Make scripts executable

## Option 2: Manual Deployment via VNC

### Step 1: Copy Files via VNC
1. Open VNC Viewer and connect to 192.168.54.181
2. Open File Manager on Pi
3. On Mac, drag the `parallel_flash_esp32` folder to VNC window
   OR use VNC's file transfer feature
   OR copy to a USB drive and plug into Pi

### Step 2: Open Terminal on Pi (via VNC)
1. Right-click desktop → Terminal
2. Navigate to the project:
   ```bash
   cd ~/parallel_flash_esp32
   ```

### Step 3: Install Dependencies
```bash
# Update system packages
sudo apt update

# Install required system packages
sudo apt install -y python3-pip python3-venv
# Note: PyQt6 will be installed via pip (not available in apt repos)

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make flashd.py executable
chmod +x flashd.py
```

## Option 3: Manual Deployment via SSH

### Step 1: Copy Files
```bash
cd /Users/quangan/Documents/Sandbox/parallel_flash_esp32
scp -r . pi@192.168.54.181:~/parallel_flash_esp32
# Enter password when prompted
```

### Step 2: SSH into Pi
```bash
ssh pi@192.168.54.181
```

### Step 3: Setup (same as Option 2, Step 3)
```bash
cd ~/parallel_flash_esp32
sudo apt update
sudo apt install -y python3-pip python3-venv
# Note: PyQt6 will be installed via pip (not available in apt repos)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
chmod +x flashd.py
```

## Using the Tool

### Via VNC (GUI Mode - Best Experience!)
1. Connect via VNC to 192.168.54.181
2. Open terminal on Pi
3. Run:
   ```bash
   cd ~/parallel_flash_esp32
   source venv/bin/activate
   ./flashd.py gui
   ```
4. The GUI will open on the Pi's desktop - you'll see it in VNC!

### Via SSH (CLI Mode)
```bash
# SSH into Pi
ssh pi@192.168.54.181

# Navigate and activate
cd ~/parallel_flash_esp32
source venv/bin/activate

# List connected ESP32 devices
./flashd.py list

# Flash all devices
./flashd.py flash

# Flash specific device
./flashd.py flash --port /dev/ttyUSB0

# Use custom firmware
./flashd.py flash --firmware /path/to/firmware.bin
```

### Remote Commands from Mac
```bash
cd /Users/quangan/Documents/Sandbox/parallel_flash_esp32
./run_on_pi.sh 192.168.54.181 list
./run_on_pi.sh 192.168.54.181 flash
```

## Copying Firmware to Pi

Once you have the firmware binary, copy it to the Pi:

```bash
# From Mac
scp firmware.bin pi@192.168.54.181:~/parallel_flash_esp32/firmware.bin

# Or via VNC file transfer
```

Then update `config.yaml` on Pi or use `--firmware` flag:
```bash
./flashd.py flash --firmware firmware.bin
```

## Troubleshooting

### Permission Denied on /dev/ttyUSB*
```bash
sudo usermod -a -G dialout $USER
# Logout and login again
```

### GUI Won't Start
```bash
# Make sure you're running via VNC (not SSH)
# Install PyQt6 if missing
sudo apt install python3-pyqt6
```

### Device Not Detected
```bash
# Check USB devices
ls -la /dev/ttyUSB* /dev/ttyACM*

# Test with esptool directly
esptool.py --port /dev/ttyUSB0 chip_id
```

