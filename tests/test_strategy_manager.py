"""Tests for DupeClean strategy manager module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.strategy_manager import (
    STRATEGIES,
    apply_strategy,
    apply_strategy_to_all,
    format_strategy_results,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


def _make_group() -> DuplicateGroup:
    return DuplicateGroup(
        group_id=0,
        hash_value="abc",
        file_size=100,
        files=[
            _fi("/very/long/nested/path/file.txt", 100, 100),
            _fi("/short/f.txt", 100, 200),
            _fi("/medium/path/file.txt", 100, 150),
        ],
    )


class TestApplyStrategy:
    def test_shortest(self):
        group = _make_group()
        result = apply_strategy(group, "shortest")
        assert result.strategy == "Shortest Path"
        assert result.keeper.path.name == "f.txt"

    def test_newest(self):
        group = _make_group()
        result = apply_strategy(group, "newest")
        assert result.strategy == "Newest"
        assert result.keeper.mtime == 200

    def test_oldest(self):
        group = _make_group()
        result = apply_strategy(group, "oldest")
        assert result.strategy == "Oldest"
        assert result.keeper.mtime == 100

    def test_savings(self):
        group = _make_group()
        result = apply_strategy(group, "shortest")
        assert result.savings == 200  # 2 files * 100 each


class TestApplyStrategyToAll:
    def test_basic(self):
        groups = [_make_group()]
        results = apply_strategy_to_all(groups, "shortest")
        assert len(results) == 1


class TestStrategies:
    def test_all_strategies_exist(self):
        expected = {"shortest", "newest", "oldest", "deepest", "shallowest"}
        assert set(STRATEGIES.keys()) == expected


class TestStrategyResult:
    def test_to_remove_count(self):
        group = _make_group()
        result = apply_strategy(group, "shortest")
        assert len(result.to_remove) == 2


class TestFormatStrategyResults:
    def test_empty(self):
        assert "No groups" in format_strategy_results([])

    def test_with_results(self):
        results = [apply_strategy(_make_group(), "shortest")]
        text = format_strategy_results(results)
        assert "Shortest Path" in text
