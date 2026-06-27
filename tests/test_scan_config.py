"""Tests for DupeClean scan config module."""

from __future__ import annotations

from dupeclean.scan_config import (
    ScanConfig,
    create_fast_scan_config,
    create_thorough_scan_config,
    format_scan_config,
)


class TestScanConfig:
    def test_defaults(self):
        config = ScanConfig()
        assert config.follow_symlinks is False
        assert config.skip_hidden is True
        assert config.threads == 4

    def test_should_ignore(self):
        config = ScanConfig()
        assert config.should_ignore(".git") is True
        assert config.should_ignore("node_modules") is True
        assert config.should_ignore("src") is False

    def test_should_skip_size(self):
        config = ScanConfig(min_file_size=100, max_file_size=1000)
        assert config.should_skip_size(50) is True
        assert config.should_skip_size(500) is False
        assert config.should_skip_size(2000) is True

    def test_should_skip_extension(self):
        config = ScanConfig(extensions=[".py", ".txt"])
        assert config.should_skip_extension(".py") is False
        assert config.should_skip_extension(".jpg") is True

    def test_no_extension_filter(self):
        config = ScanConfig()
        assert config.should_skip_extension(".jpg") is False

    def test_to_dict(self):
        config = ScanConfig()
        d = config.to_dict()
        assert d["threads"] == 4

    def test_from_dict(self):
        data = {"threads": 8, "max_depth": 10}
        config = ScanConfig.from_dict(data)
        assert config.threads == 8
        assert config.max_depth == 10


class TestCreateFastScanConfig:
    def test_fast(self):
        config = create_fast_scan_config()
        assert config.threads == 8
        assert config.max_depth == 10


class TestCreateThoroughScanConfig:
    def test_thorough(self):
        config = create_thorough_scan_config()
        assert config.max_depth == 100
        assert config.skip_hidden is False


class TestFormatScanConfig:
    def test_basic(self):
        config = ScanConfig()
        text = format_scan_config(config)
        assert "Threads" in text
        assert "4" in text
