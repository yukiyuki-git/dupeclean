"""Tests for DupeClean dedup statistics module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_stats import (
    DedupStats,
    compute_dedup_stats,
    compute_size_distribution,
    format_dedup_stats,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
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


class TestComputeDedupStats:
    def test_basic(self):
        groups = _make_groups()
        stats = compute_dedup_stats(groups)
        assert stats.total_groups == 2
        assert stats.total_duplicates == 5
        assert stats.total_wasted > 0

    def test_empty(self):
        stats = compute_dedup_stats([])
        assert stats.total_groups == 0

    def test_largest_group(self):
        groups = _make_groups()
        stats = compute_dedup_stats(groups)
        assert stats.largest_group is not None

    def test_dedup_ratio(self):
        groups = _make_groups()
        stats = compute_dedup_stats(groups)
        assert 0 < stats.dedup_ratio < 1


class TestDedupStats:
    def test_dedup_ratio_empty(self):
        stats = DedupStats()
        assert stats.dedup_ratio == 0.0


class TestFormatDedupStats:
    def test_empty(self):
        assert "No duplicates" in format_dedup_stats(DedupStats())

    def test_with_stats(self):
        groups = _make_groups()
        stats = compute_dedup_stats(groups)
        text = format_dedup_stats(stats)
        assert "Groups" in text
        assert "Wasted" in text


class TestComputeSizeDistribution:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="a",
                file_size=500,
                files=[_fi("/a"), _fi("/b")],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="b",
                file_size=50000,
                files=[_fi("/c"), _fi("/d")],
            ),
        ]
        dist = compute_size_distribution(groups)
        assert dist["tiny (<1KB)"] == 1
        assert dist["small (1-64KB)"] == 1
