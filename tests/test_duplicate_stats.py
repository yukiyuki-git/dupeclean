"""Tests for DupeClean duplicate statistics module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.duplicate_stats import (
    DuplicateStats,
    compute_duplicate_stats,
    format_duplicate_stats,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestComputeDuplicateStats:
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
        stats = compute_duplicate_stats(groups)
        assert stats.total_groups == 2
        assert stats.total_files == 5
        assert stats.total_wasted == 4000

    def test_empty(self):
        stats = compute_duplicate_stats([])
        assert stats.total_groups == 0


class TestDuplicateStats:
    def test_wasted_display(self):
        stats = DuplicateStats(total_wasted=1024)
        assert "B" in stats.wasted_display

    def test_dedup_ratio(self):
        stats = DuplicateStats(total_files=10, total_wasted=500, avg_file_size=100)
        assert stats.dedup_ratio > 0


class TestFormatDuplicateStats:
    def test_empty(self):
        stats = DuplicateStats()
        assert "No duplicates" in format_duplicate_stats(stats)

    def test_with_stats(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        stats = compute_duplicate_stats(groups)
        text = format_duplicate_stats(stats)
        assert "Groups:" in text
