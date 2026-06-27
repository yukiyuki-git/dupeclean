"""Tests for DupeClean dedup configuration module."""

from __future__ import annotations

from dupeclean.dedup_config import (
    DedupConfig,
    create_balanced_config,
    create_fast_config,
    create_thorough_config,
    format_config,
)


class TestDedupConfig:
    def test_defaults(self):
        config = DedupConfig()
        assert config.hash_algorithm == "xxhash"
        assert config.threads == 4
        assert config.dry_run is True

    def test_to_dict(self):
        config = DedupConfig()
        d = config.to_dict()
        assert d["hash_algorithm"] == "xxhash"
        assert d["threads"] == 4

    def test_from_dict(self):
        data = {"hash_algorithm": "md5", "threads": 8}
        config = DedupConfig.from_dict(data)
        assert config.hash_algorithm == "md5"
        assert config.threads == 8

    def test_from_dict_unknown_key(self):
        data = {"unknown_key": "value"}
        config = DedupConfig.from_dict(data)
        # Should not crash
        assert config.hash_algorithm == "xxhash"


class TestCreateFastConfig:
    def test_fast(self):
        config = create_fast_config()
        assert config.hash_algorithm == "xxhash"
        assert config.threads == 8
        assert config.use_prefilter is True


class TestCreateThoroughConfig:
    def test_thorough(self):
        config = create_thorough_config()
        assert config.hash_algorithm == "sha256"
        assert config.use_prefilter is False
        assert config.use_cache is False


class TestCreateBalancedConfig:
    def test_balanced(self):
        config = create_balanced_config()
        assert config.hash_algorithm == "xxhash"
        assert config.threads == 4


class TestFormatConfig:
    def test_basic(self):
        config = DedupConfig()
        text = format_config(config)
        assert "xxhash" in text
        assert "4" in text

    def test_custom(self):
        config = DedupConfig(hash_algorithm="md5", threads=8)
        text = format_config(config)
        assert "md5" in text
        assert "8" in text
