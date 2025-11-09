#!/usr/bin/env python3
"""
Parallel ESP32 Flash Daemon - CLI Entry Point

This daemon manages concurrent ESP32 flashing operations.
Can run in headless mode or launch GUI.
"""
import argparse
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional

from core import (
    Config,
    ESP32Flasher,
    DeviceManager,
    FlashLogger,
    FlashDatabase,
    FlashResult
)


class FlashDaemon:
    """Main daemon managing flash operations."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.logger = FlashLogger()
        self.log = self.logger.get_logger("flashd")
        self.db = FlashDatabase()
        self.device_manager = DeviceManager()
        self.flasher = ESP32Flasher(
            chip=self.config.chip,
            baud_rate=self.config.baud_rate,
            verify=self.config.verify
        )
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.active_flashes: Dict[str, asyncio.Task] = {}

    def flash_device(self, port: str, firmware_path: Optional[str] = None) -> FlashResult:
        """Flash a single device.

        Args:
            port: Device port path
            firmware_path: Override firmware path (uses config default if None)

        Returns:
            FlashResult object
        """
        fw_path = firmware_path or self.config.firmware_path
        port_log = self.logger.get_port_logger(port)

        port_log.info(f"Starting flash operation on {port}")
        port_log.info(f"Firmware: {fw_path}")

        # Create session log
        session_log = self.logger.create_session_log(port)

        # Execute flash
        result = self.flasher.flash_firmware(
            port=port,
            firmware_path=fw_path,
            offset=self.config.flash_offset,
            progress_callback=lambda p: port_log.debug(f"Progress: {p}%")
        )

        # Save session log
        with open(session_log, 'w') as f:
            f.write(result.log_output)

        # Log to database
        self.db.add_record(
            port=port,
            status='success' if result.success else 'fail',
            mac=result.mac,
            chip_type=result.chip_type,
            duration=result.duration,
            firmware=fw_path,
            log_path=str(session_log),
            error_msg=result.error_msg
        )

        if result.success:
            port_log.info(f"✓ Flash successful - MAC: {result.mac} - {result.duration:.2f}s")
        else:
            port_log.error(f"✗ Flash failed - {result.error_msg}")

        return result

    def flash_all_devices(self, firmware_path: Optional[str] = None) -> Dict[str, FlashResult]:
        """Flash all connected devices in parallel.

        Args:
            firmware_path: Override firmware path

        Returns:
            Dict mapping port to FlashResult
        """
        devices = self.device_manager.scan_devices()

        if not devices:
            self.log.warning("No devices found")
            return {}

        self.log.info(f"Found {len(devices)} device(s): {devices}")

        # Submit all flash tasks
        futures = {
            port: self.executor.submit(self.flash_device, port, firmware_path)
            for port in devices
        }

        # Collect results
        results = {}
        for port, future in futures.items():
            try:
                results[port] = future.result(timeout=300)  # 5 min timeout per device
            except Exception as e:
                self.log.error(f"Flash failed for {port}: {e}")
                results[port] = FlashResult(
                    success=False,
                    port=port,
                    error_msg=str(e)
                )

        return results

    def monitor_mode(self) -> None:
        """Run in continuous monitoring mode - flash devices as they're plugged in."""
        self.log.info("Starting monitor mode - flash devices as they connect")
        self.log.info("Press Ctrl+C to stop")

        def on_device_added(port: str):
            self.log.info(f"Device connected: {port}")
            # Flash in background
            self.executor.submit(self.flash_device, port)

        def on_device_removed(port: str):
            self.log.info(f"Device disconnected: {port}")

        self.device_manager.register_callback('add', on_device_added)
        self.device_manager.register_callback('remove', on_device_removed)
        self.device_manager.start_monitoring()

        try:
            # Keep running
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            self.log.info("\nStopping monitor mode")
            self.device_manager.stop_monitoring()

    def show_statistics(self) -> None:
        """Display flash statistics."""
        stats = self.db.get_statistics()
        print("\n" + "="*50)
        print("FLASH STATISTICS")
        print("="*50)
        print(f"Total flashes:     {stats['total']}")
        print(f"Successful:        {stats['success']}")
        print(f"Failed:            {stats['fail']}")
        if stats['total'] > 0:
            success_rate = (stats['success'] / stats['total']) * 100
            print(f"Success rate:      {success_rate:.1f}%")
        print("="*50 + "\n")

    def list_devices(self) -> None:
        """List connected devices."""
        devices = self.device_manager.scan_devices()
        print(f"\nFound {len(devices)} device(s):")
        for device in devices:
            print(f"  - {device}")
        print()

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        self.db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parallel ESP32 Flash Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Configuration file path'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # flash command
    flash_parser = subparsers.add_parser('flash', help='Flash device(s)')
    flash_parser.add_argument(
        '-p', '--port',
        help='Specific port to flash (default: all devices)'
    )
    flash_parser.add_argument(
        '-f', '--firmware',
        help='Firmware file path (overrides config)'
    )

    # monitor command
    subparsers.add_parser('monitor', help='Monitor and auto-flash on device connect')

    # list command
    subparsers.add_parser('list', help='List connected devices')

    # stats command
    subparsers.add_parser('stats', help='Show flash statistics')

    # gui command
    subparsers.add_parser('gui', help='Launch GUI interface')

    args = parser.parse_args()

    # Create daemon instance
    daemon = FlashDaemon(config_path=args.config)

    try:
        if args.command == 'flash':
            if args.port:
                result = daemon.flash_device(args.port, args.firmware)
                sys.exit(0 if result.success else 1)
            else:
                results = daemon.flash_all_devices(args.firmware)
                all_success = all(r.success for r in results.values())
                sys.exit(0 if all_success else 1)

        elif args.command == 'monitor':
            daemon.monitor_mode()

        elif args.command == 'list':
            daemon.list_devices()

        elif args.command == 'stats':
            daemon.show_statistics()

        elif args.command == 'gui':
            # Import GUI here to avoid dependency when running headless
            try:
                from gui.main_window import run_gui
                run_gui(daemon)
            except ImportError as e:
                print(f"Error: GUI dependencies not available: {e}")
                print("Install with: pip install PyQt6")
                sys.exit(1)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        daemon.cleanup()


if __name__ == '__main__':
    main()
