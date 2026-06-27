"""Tests for DupeClean detailed group statistics module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_detailed_stats import (
    DetailedGroupStats,
    compute_detailed_stats,
    format_detailed_stats,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestComputeDetailedStats:
    def test_basic(self):
        groups = [_group(0, 1000, 3), _group(1, 2000, 2)]
        stats = compute_detailed_stats(groups)
        assert stats.total_groups == 2
        assert stats.total_files == 5
        assert stats.total_wasted == 4000  # 2000 + 2000

    def test_empty(self):
        stats = compute_detailed_stats([])
        assert stats.total_groups == 0

    def test_largest_group(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        stats = compute_detailed_stats(groups)
        assert stats.largest_group_id == 1

    def test_most_wasted(self):
        groups = [_group(0, 100, 2), _group(1, 1000, 3)]
        stats = compute_detailed_stats(groups)
        assert stats.most_wasted_group_id == 1

    def test_dedup_ratio(self):
        groups = [_group(0, 100, 3)]
        stats = compute_detailed_stats(groups)
        assert 0 < stats.dedup_ratio < 1


class TestDetailedGroupStats:
    def test_wasted_display(self):
        stats = DetailedGroupStats(total_wasted=1024)
        assert "B" in stats.wasted_display


class TestFormatDetailedStats:
    def test_empty(self):
        assert "No duplicate" in format_detailed_stats(DetailedGroupStats())

    def test_basic(self):
        groups = [_group(0, 100, 3)]
        stats = compute_detailed_stats(groups)
        text = format_detailed_stats(stats)
        assert "Groups:" in text
        assert "Wasted:" in text
