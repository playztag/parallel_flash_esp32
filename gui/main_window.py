"""Main GUI window for parallel ESP32 flasher."""
import sys
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QTextEdit, QLabel, QFileDialog,
    QMessageBox, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont

from gui.widgets import PortWidget
from core import FlashResult


class FlashWorker(QThread):
    """Worker thread for flashing operation."""

    finished = pyqtSignal(str, FlashResult)
    progress = pyqtSignal(str, int)
    chip_info = pyqtSignal(str, str, str)  # port, chip_type, mac

    def __init__(self, daemon, port: str, firmware_path: Optional[str] = None):
        super().__init__()
        self.daemon = daemon
        self.port = port
        self.firmware_path = firmware_path

    def run(self):
        """Execute flash operation."""
        # Get chip info first
        chip_type, mac = self.daemon.flasher.get_chip_info(self.port)
        if chip_type or mac:
            self.chip_info.emit(self.port, chip_type or "Unknown", mac or "Unknown")

        # Flash with progress callback
        def progress_cb(value):
            self.progress.emit(self.port, value)

        result = self.daemon.flasher.flash_firmware(
            port=self.port,
            firmware_path=self.firmware_path or self.daemon.config.firmware_path,
            offset=self.daemon.config.flash_offset,
            progress_callback=progress_cb
        )

        self.finished.emit(self.port, result)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.port_widgets: Dict[str, PortWidget] = {}
        self.flash_workers: Dict[str, FlashWorker] = {}
        self.current_firmware = daemon.config.firmware_path

        self._init_ui()
        self._setup_device_monitoring()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Parallel ESP32 Flash Station")
        self.setMinimumSize(1000, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Toolbar
        self._create_toolbar()

        # Status bar
        self.status_label = QLabel(f"Firmware: {self.current_firmware}")
        main_layout.addWidget(self.status_label)

        # Statistics display
        self.stats_label = QLabel()
        self._update_stats()
        main_layout.addWidget(self.stats_label)

        # Content layout (grid + console)
        content_layout = QHBoxLayout()

        # Port grid (left side)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_widget.setLayout(self.grid_layout)
        content_layout.addWidget(self.grid_widget, stretch=2)

        # Console log (right side)
        console_widget = QWidget()
        console_layout = QVBoxLayout()
        console_label = QLabel("Console Log")
        font = QFont()
        font.setBold(True)
        console_label.setFont(font)
        console_layout.addWidget(console_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumWidth(350)
        console_layout.addWidget(self.console)

        # Clear console button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.console.clear)
        console_layout.addWidget(clear_btn)

        console_widget.setLayout(console_layout)
        content_layout.addWidget(console_widget, stretch=1)

        main_layout.addLayout(content_layout)

        # Refresh devices initially
        self.refresh_devices()

    def _create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Refresh devices
        refresh_action = QAction("🔄 Refresh Devices", self)
        refresh_action.triggered.connect(self.refresh_devices)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # Flash all
        flash_all_action = QAction("⚡ Flash All", self)
        flash_all_action.triggered.connect(self.flash_all)
        toolbar.addAction(flash_all_action)

        # Stop all
        stop_action = QAction("🛑 Stop All", self)
        stop_action.triggered.connect(self.stop_all)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Select firmware
        firmware_action = QAction("📁 Select Firmware", self)
        firmware_action.triggered.connect(self.select_firmware)
        toolbar.addAction(firmware_action)

        toolbar.addSeparator()

        # Reset stats
        reset_action = QAction("🔢 Reset Stats", self)
        reset_action.triggered.connect(self.reset_stats)
        toolbar.addAction(reset_action)

    def _setup_device_monitoring(self):
        """Setup automatic device monitoring."""
        self.device_manager = self.daemon.device_manager

        # Register callbacks
        self.device_manager.register_callback('add', self._on_device_added)
        self.device_manager.register_callback('remove', self._on_device_removed)

        # Start monitoring
        self.device_manager.start_monitoring()

        # Periodic refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _on_device_added(self, port: str):
        """Handle device added event."""
        self.log(f"Device connected: {port}")
        self.refresh_devices()

    def _on_device_removed(self, port: str):
        """Handle device removed event."""
        self.log(f"Device disconnected: {port}")
        self.refresh_devices()

    def refresh_devices(self):
        """Refresh device list and update grid."""
        devices = self.device_manager.scan_devices()

        # Remove widgets for disconnected devices
        for port in list(self.port_widgets.keys()):
            if port not in devices:
                widget = self.port_widgets.pop(port)
                self.grid_layout.removeWidget(widget)
                widget.deleteLater()

        # Add widgets for new devices
        for port in devices:
            if port not in self.port_widgets:
                self._add_port_widget(port)

        self._reorganize_grid()

    def _add_port_widget(self, port: str):
        """Add a port widget to the grid."""
        widget = PortWidget(port)
        widget.clicked.connect(self.on_port_clicked)
        self.port_widgets[port] = widget

    def _reorganize_grid(self):
        """Reorganize grid layout based on number of devices."""
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Calculate grid dimensions (prefer 3-4 columns)
        num_devices = len(self.port_widgets)
        if num_devices == 0:
            return

        cols = min(4, num_devices)
        rows = (num_devices + cols - 1) // cols

        # Add widgets to grid
        for idx, (port, widget) in enumerate(sorted(self.port_widgets.items())):
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(widget, row, col)

    def on_port_clicked(self, port: str):
        """Handle port widget click - flash single device."""
        self.flash_device(port)

    def flash_device(self, port: str):
        """Flash a single device."""
        if port in self.flash_workers and self.flash_workers[port].isRunning():
            self.log(f"Flash already in progress for {port}")
            return

        widget = self.port_widgets.get(port)
        if not widget:
            return

        widget.set_status('flashing')
        widget.set_progress(0)
        self.log(f"Starting flash: {port}")

        # Create worker thread
        worker = FlashWorker(self.daemon, port, self.current_firmware)
        worker.chip_info.connect(self._on_chip_info)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_flash_finished)
        worker.start()

        self.flash_workers[port] = worker

    def flash_all(self):
        """Flash all connected devices."""
        if not self.port_widgets:
            self.log("No devices connected")
            return

        self.log("Starting flash for all devices...")
        for port in self.port_widgets.keys():
            self.flash_device(port)

    def stop_all(self):
        """Stop all flashing operations."""
        for worker in self.flash_workers.values():
            if worker.isRunning():
                worker.terminate()
                worker.wait()

        for widget in self.port_widgets.values():
            if widget.status == 'flashing':
                widget.set_status('idle', 'Stopped')

        self.log("All operations stopped")

    def _on_chip_info(self, port: str, chip_type: str, mac: str):
        """Handle chip info received."""
        widget = self.port_widgets.get(port)
        if widget:
            widget.set_chip_info(chip_type, mac)

    def _on_progress(self, port: str, value: int):
        """Handle progress update."""
        widget = self.port_widgets.get(port)
        if widget:
            widget.set_progress(value)

    def _on_flash_finished(self, port: str, result: FlashResult):
        """Handle flash completion."""
        widget = self.port_widgets.get(port)
        if widget:
            if result.success:
                widget.set_status('success')
                widget.set_progress(100)
                self.log(f"✓ {port} - Success ({result.duration:.2f}s)")
            else:
                widget.set_status('fail', result.error_msg or "Failed")
                self.log(f"✗ {port} - Failed: {result.error_msg}")

        # Update statistics
        self._update_stats()

        # Clean up worker
        if port in self.flash_workers:
            del self.flash_workers[port]

    def select_firmware(self):
        """Open file dialog to select firmware."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Firmware",
            "",
            "Binary Files (*.bin);;All Files (*)"
        )

        if file_path:
            self.current_firmware = file_path
            self.daemon.config.firmware_path = file_path
            self.daemon.config.save()
            self.status_label.setText(f"Firmware: {file_path}")
            self.log(f"Firmware selected: {file_path}")

    def reset_stats(self):
        """Reset flash statistics."""
        reply = QMessageBox.question(
            self,
            "Reset Statistics",
            "Are you sure you want to reset all statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.daemon.db.reset_statistics()
            self._update_stats()
            self.log("Statistics reset")

    def _update_stats(self):
        """Update statistics display."""
        stats = self.daemon.db.get_statistics()
        self.stats_label.setText(
            f"Total: {stats['total']} | "
            f"Success: {stats['success']} | "
            f"Failed: {stats['fail']}"
        )

    def log(self, message: str):
        """Add message to console log."""
        self.console.append(message)

    def closeEvent(self, event):
        """Handle window close event."""
        self.device_manager.stop_monitoring()
        self.stop_all()
        self.daemon.cleanup()
        event.accept()


def run_gui(daemon):
    """Run GUI application.

    Args:
        daemon: FlashDaemon instance
    """
    app = QApplication(sys.argv)
    window = MainWindow(daemon)
    window.show()
    sys.exit(app.exec())
