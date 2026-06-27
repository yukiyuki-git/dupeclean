"""Tests for DupeClean scheduler config module."""

from __future__ import annotations

from dupeclean.scheduler_config import (
    SchedulerConfig,
    create_default_config,
    create_fast_config,
    format_config,
)


class TestSchedulerConfig:
    def test_defaults(self):
        config = SchedulerConfig()
        assert config.max_concurrent == 1
        assert config.retry_count == 3
        assert config.enabled is True

    def test_to_dict(self):
        config = SchedulerConfig()
        d = config.to_dict()
        assert d["max_concurrent"] == 1
        assert d["retry_count"] == 3

    def test_from_dict(self):
        data = {"max_concurrent": 4, "retry_count": 1}
        config = SchedulerConfig.from_dict(data)
        assert config.max_concurrent == 4
        assert config.retry_count == 1

    def test_from_dict_unknown_key(self):
        data = {"unknown": "value"}
        config = SchedulerConfig.from_dict(data)
        assert config.max_concurrent == 1  # Default


class TestCreateConfigs:
    def test_default(self):
        config = create_default_config()
        assert config.max_concurrent == 1

    def test_fast(self):
        config = create_fast_config()
        assert config.max_concurrent == 4


class TestFormatConfig:
    def test_basic(self):
        config = SchedulerConfig()
        text = format_config(config)
        assert "Scheduler" in text
        assert "1" in text
