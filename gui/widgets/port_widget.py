"""Port status widget for GUI."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class PortWidget(QWidget):
    """Widget displaying status for a single port."""

    clicked = pyqtSignal(str)  # Emits port name when clicked

    def __init__(self, port: str, parent=None):
        super().__init__(parent)
        self.port = port
        self.status = "idle"
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Port label
        self.port_label = QLabel(self.port)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.port_label.setFont(font)
        self.port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Chip info label
        self.chip_label = QLabel("---")
        self.chip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_small = QFont()
        font_small.setPointSize(8)
        self.chip_label.setFont(font_small)

        # MAC address label
        self.mac_label = QLabel("MAC: ---")
        self.mac_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mac_label.setFont(font_small)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Status label
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(font_small)

        # Add widgets to layout
        layout.addWidget(self.port_label)
        layout.addWidget(self.chip_label)
        layout.addWidget(self.mac_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self._update_style()

    def set_status(self, status: str, message: str = ""):
        """Set widget status.

        Args:
            status: One of 'idle', 'flashing', 'success', 'fail'
            message: Optional status message
        """
        self.status = status

        if message:
            self.status_label.setText(message)
        else:
            status_text = {
                'idle': 'Idle',
                'flashing': 'Flashing...',
                'success': '✓ Success',
                'fail': '✗ Failed'
            }
            self.status_label.setText(status_text.get(status, status))

        self._update_style()

    def set_chip_info(self, chip_type: str = None, mac: str = None):
        """Set chip information."""
        if chip_type:
            self.chip_label.setText(chip_type)
        if mac:
            self.mac_label.setText(f"MAC: {mac}")

    def set_progress(self, value: int):
        """Set progress bar value (0-100)."""
        self.progress_bar.setValue(value)

    def reset(self):
        """Reset widget to initial state."""
        self.status = "idle"
        self.chip_label.setText("---")
        self.mac_label.setText("MAC: ---")
        self.progress_bar.setValue(0)
        self.status_label.setText("Idle")
        self._update_style()

    def _update_style(self):
        """Update widget styling based on status."""
        colors = {
            'idle': '#FFFFFF',      # White
            'flashing': '#FFF9C4',  # Yellow
            'success': '#C8E6C9',   # Green
            'fail': '#FFCDD2'       # Red
        }

        border_colors = {
            'idle': '#CCCCCC',
            'flashing': '#FBC02D',
            'success': '#388E3C',
            'fail': '#D32F2F'
        }

        bg_color = colors.get(self.status, '#FFFFFF')
        border_color = border_colors.get(self.status, '#CCCCCC')

        self.setStyleSheet(f"""
            PortWidget {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
        """)

    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.port)
        super().mousePressEvent(event)
