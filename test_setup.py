#!/usr/bin/env python3
"""Test setup - check for ESP32 devices and dependencies."""

import sys
import subprocess

print("=" * 60)
print("Parallel ESP32 Flash Station - Setup Test")
print("=" * 60)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")

# Check for esptool
try:
    result = subprocess.run(['esptool.py', 'version'],
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.strip().split('\n')[0]
        print(f"✓ esptool.py: {version}")
    else:
        print("✗ esptool.py not found - run: pip install esptool")
except FileNotFoundError:
    print("✗ esptool.py not found - run: pip install esptool")
except Exception as e:
    print(f"✗ esptool.py error: {e}")

# Check for PyQt6
try:
    import PyQt6
    print(f"✓ PyQt6 installed")
except ImportError:
    print("⚠ PyQt6 not installed - GUI won't work. Install: pip install PyQt6")

# Check for pyudev (Linux only)
try:
    import pyudev
    print(f"✓ pyudev installed (hotplug detection)")
except ImportError:
    print("⚠ pyudev not installed - will use polling fallback")

# Check for devices
print("\n" + "=" * 60)
print("Scanning for ESP32 devices...")
print("=" * 60)

from core import DeviceManager
dm = DeviceManager()
devices = dm.scan_devices()

if devices:
    print(f"\n✓ Found {len(devices)} device(s):")
    for dev in devices:
        print(f"  - {dev}")

        # Try to get chip info
        try:
            result = subprocess.run(
                ['esptool.py', '--port', dev, 'chip_id'],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout + result.stderr

            # Parse chip type
            if 'Chip is' in output:
                for line in output.split('\n'):
                    if 'Chip is' in line:
                        print(f"    {line.strip()}")
            if 'MAC:' in output:
                for line in output.split('\n'):
                    if 'MAC:' in line:
                        print(f"    {line.strip()}")
        except Exception as e:
            print(f"    Unable to read chip info: {e}")
else:
    print("\n✗ No devices found!")
    print("\nTroubleshooting:")
    print("  - Check if ESP32 is connected via USB")
    print("  - On Linux: Check permissions (add user to 'dialout' group)")
    print("  - Try: ls /dev/ttyUSB* /dev/ttyACM* /dev/cu.*")

print("\n" + "=" * 60)
