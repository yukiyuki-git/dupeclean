"""Tests for DupeClean dedup engine module."""

from __future__ import annotations

from dupeclean.engine import (
    DedupConfig,
    DedupEngineResult,
    create_engine_config,
    format_engine_result,
)


class TestDedupConfig:
    def test_defaults(self):
        config = DedupConfig()
        assert config.hash_algorithm == "xxhash"
        assert config.threads == 4


class TestCreateEngineConfig:
    def test_fast(self):
        config = create_engine_config(fast=True)
        assert config.threads == 8
        assert config.use_prefilter is True

    def test_thorough(self):
        config = create_engine_config(thorough=True)
        assert config.hash_algorithm == "sha256"
        assert config.use_prefilter is False

    def test_default(self):
        config = create_engine_config()
        assert config.hash_algorithm == "xxhash"


class TestDedupEngineResult:
    def test_wasted_display(self):
        result = DedupEngineResult(total_wasted=1024)
        assert "B" in result.wasted_display

    def test_dupe_percentage(self):
        result = DedupEngineResult(files_scanned=100, total_duplicates=25)
        assert result.dupe_percentage == 25.0

    def test_zero_scanned(self):
        result = DedupEngineResult()
        assert result.dupe_percentage == 0.0


class TestFormatEngineResult:
    def test_basic(self):
        result = DedupEngineResult(
            files_scanned=1000,
            size_groups=50,
            hash_groups=20,
            confirmed_groups=10,
            total_duplicates=30,
            total_wasted=50000,
            scan_duration=1.5,
            hash_duration=3.0,
            total_duration=4.5,
        )
        text = format_engine_result(result)
        assert "1,000" in text
        assert "50" in text
        assert "1.50s" in text
