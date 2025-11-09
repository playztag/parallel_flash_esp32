"""Logging utilities for parallel ESP32 flasher."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class FlashLogger:
    """Manages logging for flashing operations."""

    def __init__(self, log_dir: str = "static/logs", console: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.console = console
        self._loggers = {}

    def get_logger(self, name: str = "zflash") -> logging.Logger:
        """Get or create a logger instance."""
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # File handler - daily log file
        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        if self.console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        self._loggers[name] = logger
        return logger

    def get_port_logger(self, port: str) -> logging.Logger:
        """Get a logger for a specific port."""
        port_name = port.replace('/', '_')
        logger_name = f"zflash.{port_name}"
        return self.get_logger(logger_name)

    def create_session_log(self, port: str) -> Path:
        """Create a session-specific log file for detailed output."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        port_name = port.replace('/', '_')
        log_file = self.log_dir / f"{port_name}_{timestamp}.log"
        return log_file
