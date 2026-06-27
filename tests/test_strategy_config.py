"""Tests for DupeClean strategy config module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.strategy_config import (
    BUILTIN_STRATEGIES,
    CleanupStrategyConfig,
    format_strategy,
    get_strategy,
    list_strategies,
)


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupStrategyConfig:
    def test_matches_file_default(self):
        strategy = get_strategy("default")
        assert strategy.matches_file(_fi("/a.txt", 100)) is True

    def test_min_file_size(self):
        strategy = CleanupStrategyConfig(
            name="test", description="test", keep_rule="shortest", min_file_size=1000
        )
        assert strategy.matches_file(_fi("/a", 500)) is False
        assert strategy.matches_file(_fi("/a", 1500)) is True

    def test_max_file_size(self):
        strategy = CleanupStrategyConfig(
            name="test", description="test", keep_rule="shortest", max_file_size=1000
        )
        assert strategy.matches_file(_fi("/a", 500)) is True
        assert strategy.matches_file(_fi("/a", 1500)) is False

    def test_extensions_filter(self):
        strategy = CleanupStrategyConfig(
            name="test", description="test", keep_rule="shortest", extensions=[".jpg", ".png"]
        )
        assert strategy.matches_file(_fi("/a.jpg", 100)) is True
        assert strategy.matches_file(_fi("/a.txt", 100)) is False


class TestGetStrategy:
    def test_default(self):
        strategy = get_strategy("default")
        assert strategy.name == "Default"

    def test_unknown_falls_back(self):
        strategy = get_strategy("unknown")
        assert strategy.name == "Default"


class TestListStrategies:
    def test_has_strategies(self):
        strategies = list_strategies()
        assert len(strategies) >= 4


class TestBuiltinStrategies:
    def test_all_exist(self):
        expected = {"default", "aggressive", "conservative", "media"}
        assert set(BUILTIN_STRATEGIES.keys()) == expected


class TestFormatStrategy:
    def test_basic(self):
        strategy = get_strategy("default")
        text = format_strategy(strategy)
        assert "Default" in text
        assert "shortest" in text
