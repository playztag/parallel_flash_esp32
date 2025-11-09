"""ESP32 flasher module wrapping esptool functionality."""
import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import serial


@dataclass
class FlashResult:
    """Result of a flash operation."""
    success: bool
    port: str
    mac: Optional[str] = None
    chip_type: Optional[str] = None
    duration: float = 0.0
    error_msg: Optional[str] = None
    log_output: str = ""


class ESP32Flasher:
    """Handles ESP32 flashing operations using esptool."""

    def __init__(self, chip: str = "esp32", baud_rate: int = 921600, verify: bool = True):
        self.chip = chip
        self.baud_rate = baud_rate
        self.verify = verify

    def get_chip_info(self, port: str) -> Tuple[Optional[str], Optional[str]]:
        """Get chip type and MAC address from device.

        Returns:
            Tuple of (chip_type, mac_address)
        """
        try:
            cmd = [
                "esptool.py",
                "--port", port,
                "--baud", str(self.baud_rate),
                "chip_id"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout + result.stderr

            # Extract chip type
            chip_match = re.search(r'Chip is (ESP[^\s]+)', output)
            chip_type = chip_match.group(1) if chip_match else None

            # Extract MAC address
            mac_match = re.search(r'MAC: ([0-9a-f:]+)', output, re.IGNORECASE)
            mac = mac_match.group(1) if mac_match else None

            return chip_type, mac

        except Exception as e:
            return None, None

    def flash_firmware(
        self,
        port: str,
        firmware_path: str,
        offset: int = 0x1000,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> FlashResult:
        """Flash firmware to ESP32 device.

        Args:
            port: Serial port device path
            firmware_path: Path to firmware binary
            offset: Flash offset address
            progress_callback: Optional callback for progress updates (0-100)

        Returns:
            FlashResult with operation details
        """
        start_time = time.time()
        result = FlashResult(success=False, port=port)

        # Validate firmware file
        firmware = Path(firmware_path)
        if not firmware.exists():
            result.error_msg = f"Firmware file not found: {firmware_path}"
            return result

        try:
            # Get chip info first
            chip_type, mac = self.get_chip_info(port)
            result.chip_type = chip_type
            result.mac = mac

            # Build esptool command
            cmd = [
                "esptool.py",
                "--chip", self.chip,
                "--port", port,
                "--baud", str(self.baud_rate),
                "write_flash"
            ]

            if self.verify:
                cmd.append("--verify")

            cmd.extend(["-z", hex(offset), str(firmware)])

            # Execute flash operation
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            output_lines = []
            for line in process.stdout:
                output_lines.append(line)

                # Parse progress from esptool output
                if progress_callback:
                    # esptool outputs: Writing at 0x00001000... (X %)
                    progress_match = re.search(r'\((\d+)\s*%\)', line)
                    if progress_match:
                        progress = int(progress_match.group(1))
                        progress_callback(progress)

            process.wait()
            result.log_output = ''.join(output_lines)

            # Check result
            if process.returncode == 0:
                result.success = True
            else:
                result.error_msg = f"esptool failed with code {process.returncode}"

        except subprocess.TimeoutExpired:
            result.error_msg = "Flash operation timed out"
        except Exception as e:
            result.error_msg = f"Flash error: {str(e)}"

        result.duration = time.time() - start_time
        return result

    def erase_flash(self, port: str) -> bool:
        """Erase entire flash memory.

        Args:
            port: Serial port device path

        Returns:
            True if erase successful
        """
        try:
            cmd = [
                "esptool.py",
                "--chip", self.chip,
                "--port", port,
                "--baud", str(self.baud_rate),
                "erase_flash"
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0

        except Exception:
            return False

    def verify_port(self, port: str) -> bool:
        """Verify that a port has an ESP32 device connected.

        Args:
            port: Serial port device path

        Returns:
            True if ESP32 device detected
        """
        try:
            # Try to open serial port
            with serial.Serial(port, self.baud_rate, timeout=1):
                pass

            # Try to get chip info
            chip_type, _ = self.get_chip_info(port)
            return chip_type is not None

        except Exception:
            return False
