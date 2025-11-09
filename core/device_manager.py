"""Device detection and hotplug monitoring."""
import threading
from typing import List, Callable, Optional, Set
from pathlib import Path
import time


try:
    import pyudev
    PYUDEV_AVAILABLE = True
except ImportError:
    PYUDEV_AVAILABLE = False


class DeviceManager:
    """Manages USB device detection and hotplug events."""

    def __init__(self):
        self.devices: Set[str] = set()
        self.callbacks = {
            'add': [],
            'remove': []
        }
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self.use_pyudev = PYUDEV_AVAILABLE

    def scan_devices(self, patterns: List[str] = None) -> List[str]:
        """Scan for connected serial devices.

        Args:
            patterns: List of device patterns to match (e.g., ['ttyUSB*', 'ttyACM*'])

        Returns:
            List of device paths
        """
        if patterns is None:
            patterns = ['ttyUSB*', 'ttyACM*', 'cu.usbserial-*', 'cu.SLAB_USBtoUART*']

        devices = []
        dev_dir = Path('/dev')

        if not dev_dir.exists():
            return devices

        for pattern in patterns:
            devices.extend([str(p) for p in dev_dir.glob(pattern)])

        devices.sort()
        return devices

    def register_callback(self, event: str, callback: Callable[[str], None]) -> None:
        """Register a callback for device events.

        Args:
            event: 'add' or 'remove'
            callback: Function to call with device path
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def start_monitoring(self) -> None:
        """Start monitoring for device hotplug events."""
        if self._running:
            return

        self._running = True

        if self.use_pyudev:
            self._monitor_thread = threading.Thread(target=self._pyudev_monitor, daemon=True)
        else:
            self._monitor_thread = threading.Thread(target=self._poll_monitor, daemon=True)

        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring for device events."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

    def _pyudev_monitor(self) -> None:
        """Monitor devices using pyudev (Linux only)."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='tty')

        # Initial scan
        current_devices = set(self.scan_devices())
        self.devices = current_devices

        for device in monitor:
            if not self._running:
                break

            device_path = device.device_node
            if not device_path:
                continue

            if device.action == 'add':
                if device_path not in self.devices:
                    self.devices.add(device_path)
                    for callback in self.callbacks['add']:
                        callback(device_path)

            elif device.action == 'remove':
                if device_path in self.devices:
                    self.devices.remove(device_path)
                    for callback in self.callbacks['remove']:
                        callback(device_path)

    def _poll_monitor(self) -> None:
        """Monitor devices using polling (fallback method)."""
        # Initial scan
        self.devices = set(self.scan_devices())

        while self._running:
            time.sleep(1)  # Poll every second

            current_devices = set(self.scan_devices())

            # Detect added devices
            added = current_devices - self.devices
            for device in added:
                self.devices.add(device)
                for callback in self.callbacks['add']:
                    callback(device)

            # Detect removed devices
            removed = self.devices - current_devices
            for device in removed:
                self.devices.discard(device)
                for callback in self.callbacks['remove']:
                    callback(device)

    def get_devices(self) -> List[str]:
        """Get list of currently connected devices.

        Returns:
            List of device paths
        """
        return sorted(list(self.devices))

    def refresh(self) -> List[str]:
        """Force refresh of device list.

        Returns:
            Updated list of devices
        """
        devices = self.scan_devices()
        self.devices = set(devices)
        return devices
