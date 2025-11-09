"""Configuration management for parallel ESP32 flasher."""
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration from YAML file."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)

    def save(self) -> None:
        """Save current configuration to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    @property
    def baud_rate(self) -> int:
        return self._config.get('baud_rate', 921600)

    @property
    def chip(self) -> str:
        return self._config.get('chip', 'esp32')

    @property
    def flash_offset(self) -> int:
        return self._config.get('flash_offset', 0x1000)

    @property
    def firmware_path(self) -> str:
        return self._config.get('firmware_path', 'static/firmware/firmware.bin')

    @firmware_path.setter
    def firmware_path(self, value: str) -> None:
        self._config['firmware_path'] = value

    @property
    def verify(self) -> bool:
        return self._config.get('verify', True)

    @property
    def max_workers(self) -> int:
        return self._config.get('max_workers', 10)

    @property
    def mqtt_enabled(self) -> bool:
        return self._config.get('mqtt', {}).get('enabled', False)

    @property
    def mqtt_broker(self) -> str:
        return self._config.get('mqtt', {}).get('broker', 'localhost')

    @property
    def mqtt_topic(self) -> str:
        return self._config.get('mqtt', {}).get('topic', 'zflash/results')
