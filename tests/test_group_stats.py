"""Tests for DupeClean group stats module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_stats import (
    GroupStats,
    compute_group_stats,
    format_group_stats,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestComputeGroupStats:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a"), _fi("/b"), _fi("/c")],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="def",
                file_size=2000,
                files=[_fi("/d"), _fi("/e")],
            ),
        ]
        stats = compute_group_stats(groups)
        assert stats.total_groups == 2
        assert stats.total_files == 5
        assert stats.total_wasted == 4000

    def test_empty(self):
        stats = compute_group_stats([])
        assert stats.total_groups == 0


class TestGroupStats:
    def test_wasted_display(self):
        stats = GroupStats(total_wasted=1024)
        assert "B" in stats.wasted_display

    def test_dedup_potential(self):
        stats = GroupStats(total_files=10, total_wasted=500, avg_group_size=100)
        assert stats.dedup_potential > 0


class TestFormatGroupStats:
    def test_empty(self):
        stats = GroupStats()
        assert "No duplicate" in format_group_stats(stats)

    def test_with_stats(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        stats = compute_group_stats(groups)
        text = format_group_stats(stats)
        assert "Groups:" in text
