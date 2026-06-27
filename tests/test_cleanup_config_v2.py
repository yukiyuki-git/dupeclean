"""Tests for DupeClean cleanup config v2 module."""

from __future__ import annotations

from dupeclean.cleanup_config_v2 import (
    CleanupConfigV2,
    create_fast_cleanup_config,
    create_safe_cleanup_config,
    format_cleanup_config_v2,
)


class TestCleanupConfigV2:
    def test_defaults(self):
        config = CleanupConfigV2()
        assert config.strategy == "shortest"
        assert config.action == "hardlink"
        assert config.dry_run is True
        assert config.threads == 4

    def test_to_dict(self):
        config = CleanupConfigV2()
        d = config.to_dict()
        assert d["strategy"] == "shortest"
        assert d["threads"] == 4

    def test_from_dict(self):
        data = {"strategy": "newest", "threads": 8}
        config = CleanupConfigV2.from_dict(data)
        assert config.strategy == "newest"
        assert config.threads == 8

    def test_from_dict_unknown(self):
        data = {"unknown": "value"}
        config = CleanupConfigV2.from_dict(data)
        assert config.strategy == "shortest"


class TestCreateFastCleanupConfig:
    def test_fast(self):
        config = create_fast_cleanup_config()
        assert config.threads == 8
        assert config.verify is False


class TestCreateSafeCleanupConfig:
    def test_safe(self):
        config = create_safe_cleanup_config()
        assert config.dry_run is True
        assert config.verify is True


class TestFormatCleanupConfigV2:
    def test_basic(self):
        config = CleanupConfigV2()
        text = format_cleanup_config_v2(config)
        assert "shortest" in text
        assert "hardlink" in text
