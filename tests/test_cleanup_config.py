"""Tests for DupeClean cleanup config module."""

from __future__ import annotations

from dupeclean.cleanup_config import (
    CleanupConfig,
    create_aggressive_config,
    create_default_cleanup_config,
    create_safe_config,
    format_cleanup_config,
)


class TestCleanupConfig:
    def test_defaults(self):
        config = CleanupConfig()
        assert config.strategy == "shortest"
        assert config.action == "hardlink"
        assert config.dry_run is True

    def test_to_dict(self):
        config = CleanupConfig()
        d = config.to_dict()
        assert d["strategy"] == "shortest"
        assert d["dry_run"] is True

    def test_from_dict(self):
        data = {"strategy": "newest", "action": "delete"}
        config = CleanupConfig.from_dict(data)
        assert config.strategy == "newest"
        assert config.action == "delete"

    def test_from_dict_unknown_key(self):
        data = {"unknown": "value"}
        config = CleanupConfig.from_dict(data)
        assert config.strategy == "shortest"


class TestCreateConfigs:
    def test_default(self):
        config = create_default_cleanup_config()
        assert config.strategy == "shortest"

    def test_aggressive(self):
        config = create_aggressive_config()
        assert config.action == "delete"
        assert config.verify is False

    def test_safe(self):
        config = create_safe_config()
        assert config.dry_run is True
        assert config.backup is True


class TestFormatCleanupConfig:
    def test_basic(self):
        config = CleanupConfig()
        text = format_cleanup_config(config)
        assert "shortest" in text
        assert "hardlink" in text
