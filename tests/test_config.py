"""Tests for Config class."""

import pytest
import json
from pathlib import Path
from src.core.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_config_created(self, tmp_path):
        """Test that default config is created if not exists."""
        config_file = tmp_path / "config.json"
        config = Config(config_file)

        assert config_file.exists()
        assert config.get("api.tmdb_language") == "es-ES"

    def test_load_existing_config(self, tmp_path):
        """Test loading existing configuration."""
        config_file = tmp_path / "config.json"
        test_config = {
            "api": {"tmdb_api_key": "test_key", "tmdb_language": "en-US"},
            "organization": {"base_directory": "/test"},
        }

        with open(config_file, "w") as f:
            json.dump(test_config, f)

        config = Config(config_file)

        assert config.get("api.tmdb_api_key") == "test_key"
        assert config.get("api.tmdb_language") == "en-US"

    def test_get_nested_value(self, tmp_path):
        """Test getting nested configuration values."""
        config = Config(tmp_path / "config.json")

        value = config.get("api.tmdb_language")
        assert value == "es-ES"

        value = config.get("cache.ttl_days")
        assert value == 7

    def test_get_default_on_missing(self, tmp_path):
        """Test default value on missing key."""
        config = Config(tmp_path / "config.json")

        value = config.get("nonexistent.key", "default")
        assert value == "default"

    def test_set_value(self, tmp_path):
        """Test setting configuration values."""
        config = Config(tmp_path / "config.json")

        config.set("api.tmdb_api_key", "new_key")
        assert config.get("api.tmdb_api_key") == "new_key"

        # Verify persistence
        config2 = Config(tmp_path / "config.json")
        assert config2.get("api.tmdb_api_key") == "new_key"
