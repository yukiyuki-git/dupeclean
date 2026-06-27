"""Tests for DupeClean dedup strategy module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.strategies import (
    STRATEGIES,
    apply_strategy,
    format_decisions,
    keep_in_deepest_dir,
    keep_in_shallowest_dir,
    keep_longest_path,
    keep_newest,
    keep_oldest,
    keep_shortest_path,
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


class TestKeepShortestPath:
    def test_basic(self):
        group = _make_group()
        decision = keep_shortest_path(group)
        assert decision.strategy == "shortest_path"
        assert decision.keep.path.name == "f.txt"
        assert len(decision.remove) == 2


class TestKeepLongestPath:
    def test_basic(self):
        group = _make_group()
        decision = keep_longest_path(group)
        assert decision.strategy == "longest_path"
        assert "nested" in str(decision.keep.path)


class TestKeepNewest:
    def test_basic(self):
        group = _make_group()
        decision = keep_newest(group)
        assert decision.strategy == "newest"
        assert decision.keep.mtime == 200


class TestKeepOldest:
    def test_basic(self):
        group = _make_group()
        decision = keep_oldest(group)
        assert decision.strategy == "oldest"
        assert decision.keep.mtime == 100


class TestKeepInDeepestDir:
    def test_basic(self):
        group = _make_group()
        decision = keep_in_deepest_dir(group)
        assert decision.strategy == "deepest_dir"


class TestKeepInShallowestDir:
    def test_basic(self):
        group = _make_group()
        decision = keep_in_shallowest_dir(group)
        assert decision.strategy == "shallowest_dir"


class TestApplyStrategy:
    def test_basic(self):
        groups = [_make_group()]
        decisions = apply_strategy(groups, "shortest_path")
        assert len(decisions) == 1
        assert decisions[0].strategy == "shortest_path"

    def test_unknown_strategy(self):
        groups = [_make_group()]
        decisions = apply_strategy(groups, "unknown")
        assert len(decisions) == 1
        # Should fall back to shortest_path
        assert decisions[0].strategy == "shortest_path"


class TestStrategies:
    def test_all_strategies_exist(self):
        expected = {
            "shortest_path",
            "longest_path",
            "newest",
            "oldest",
            "deepest_dir",
            "shallowest_dir",
        }
        assert set(STRATEGIES.keys()) == expected


class TestDedupDecision:
    def test_remove_count(self):
        group = _make_group()
        decision = keep_shortest_path(group)
        assert len(decision.remove) == group.count - 1


class TestFormatDecisions:
    def test_empty(self):
        assert "No duplicate" in format_decisions([])

    def test_with_decisions(self):
        decisions = [keep_shortest_path(_make_group())]
        text = format_decisions(decisions)
        assert "shortest_path" in text
