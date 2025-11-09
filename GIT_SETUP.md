# Git Setup Instructions

## Step 1: Create Repository on GitHub/GitLab/etc

1. Go to your git hosting service (GitHub, GitLab, Bitbucket, etc.)
2. Create a new public repository (e.g., `parallel_flash_esp32`)
3. **Don't** initialize with README, .gitignore, or license (we already have these)

## Step 2: Push to Your Repository

```bash
cd /Users/quangan/Documents/Sandbox/parallel_flash_esp32

# Add your remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/parallel_flash_esp32.git
# OR if using SSH (requires SSH key setup):
# git remote add origin git@github.com:YOUR_USERNAME/parallel_flash_esp32.git

# Commit all files
git commit -m "Initial commit: Parallel ESP32 flasher with GUI"

# Push to remote
git push -u origin main
# If your default branch is 'master' instead:
# git push -u origin master
```

## Step 3: Deploy to Pi via Git

On your Raspberry Pi:

```bash
# Clone the repository
cd ~
git clone https://github.com/YOUR_USERNAME/parallel_flash_esp32.git
cd parallel_flash_esp32

# Run setup script
chmod +x setup_pi.sh
./setup_pi.sh
```

Or manually:
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/parallel_flash_esp32.git
cd parallel_flash_esp32

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv
# Note: PyQt6 will be installed via pip (not available in apt repos)

# Create venv and install packages
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make executable
chmod +x flashd.py
```

## Updating on Pi

When you make changes and push to git:

```bash
# On Pi
cd ~/parallel_flash_esp32
git pull
source venv/bin/activate
pip install -r requirements.txt  # In case requirements changed
```

## Running on Pi

```bash
cd ~/parallel_flash_esp32
source venv/bin/activate

# GUI mode (via VNC)
./flashd.py gui

# CLI mode
./flashd.py list
./flashd.py flash
```

