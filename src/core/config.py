"""Configuration management module."""

import json
from pathlib import Path
from typing import Any


class Config:
    """Manages application configuration via JSON/YAML file."""

    DEFAULT_CONFIG = {
        "api": {
            "tmdb_api_key": "",
            "tmdb_language": "es-ES",
            "use_imdb": False,
        },
        "organization": {
            "base_directory": "",
            "folder_pattern": "{title} ({year})",
            "file_pattern": "{title} - S{season:02d}E{episode:02d}",
            "create_season_folders": True,
            "replace_existing": False,
        },
        "cache": {
            "enabled": True,
            "ttl_days": 7,
            "db_path": "cache.db",
        },
        "ui": {
            "language": "es",
            "theme": "system",
            "show_preview": True,
        },
    }

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration.

        Args:
            config_path: Path to configuration file. Defaults to ~/.mediaorganizer/config.json
        """
        if config_path is None:
            config_dir = Path.home() / ".mediaorganizer"
            config_dir.mkdir(parents=True, exist_ok=True)
            self._config_path = config_dir / "config.json"
        else:
            self._config_path = Path(config_path)

        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or create default."""
        if self._config_path.exists():
            with open(self._config_path, encoding="utf-8") as f:
                return json.load(f)
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "api.tmdb_api_key")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "api.tmdb_api_key")
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self._save_config(self._config)

    @property
    def config_path(self) -> Path:
        """Return the configuration file path."""
        return self._config_path
