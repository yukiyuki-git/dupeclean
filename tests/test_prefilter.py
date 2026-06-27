"""Tests for DupeClean dedup optimization module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.prefilter import (
    PrefilterStats,
    format_prefilter_stats,
    optimize_batch_size,
    optimize_by_inode,
    optimize_by_size_prefilter,
    run_prefilter,
)


def _fi(path: str, size: int = 100, inode: int | None = None) -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    fi.inode = inode
    return fi


class TestOptimizeBySizePrefilter:
    def test_filters_unique_sizes(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 200),
            _fi("/c", 100),
            _fi("/d", 300),
        ]
        candidates, skipped = optimize_by_size_prefilter(files)
        assert len(candidates) == 2  # a and c (size 100)
        assert len(skipped) == 2  # b and d

    def test_all_same_size(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 100)]
        candidates, skipped = optimize_by_size_prefilter(files)
        assert len(candidates) == 3
        assert len(skipped) == 0

    def test_all_unique_sizes(self):
        files = [_fi("/a", 100), _fi("/b", 200), _fi("/c", 300)]
        candidates, skipped = optimize_by_size_prefilter(files)
        assert len(candidates) == 0
        assert len(skipped) == 3


class TestOptimizeByInode:
    def test_finds_hardlinks(self):
        files = [
            _fi("/a", 100, inode=1),
            _fi("/b", 100, inode=1),
            _fi("/c", 100, inode=2),
        ]
        unique, hardlinked = optimize_by_inode(files)
        assert len(unique) == 2
        assert len(hardlinked) == 1

    def test_no_inodes(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        unique, hardlinked = optimize_by_inode(files)
        assert len(unique) == 2
        assert len(hardlinked) == 0


class TestOptimizeBatchSize:
    def test_basic(self):
        assert optimize_batch_size(1000, 512) > 0

    def test_small_total(self):
        # When total < min batch, returns total
        assert optimize_batch_size(50, 512) == 50

    def test_large_total(self):
        assert optimize_batch_size(100000, 512) == 100000


class TestRunPrefilter:
    def test_basic(self):
        files = [
            _fi("/a", 100, inode=1),
            _fi("/b", 100, inode=1),
            _fi("/c", 200),
            _fi("/d", 300),
        ]
        _candidates, stats = run_prefilter(files)
        assert stats.original_count == 4
        assert stats.candidate_count < stats.original_count

    def test_empty(self):
        _candidates, stats = run_prefilter([])
        assert stats.original_count == 0


class TestPrefilterStats:
    def test_reduction_pct(self):
        stats = PrefilterStats(original_count=100, candidate_count=50)
        assert stats.reduction_pct == 50.0

    def test_zero_original(self):
        stats = PrefilterStats()
        assert stats.reduction_pct == 0.0


class TestFormatPrefilterStats:
    def test_basic(self):
        stats = PrefilterStats(
            original_count=100,
            candidate_count=60,
            skipped_count=40,
        )
        text = format_prefilter_stats(stats)
        assert "100" in text
        assert "60" in text
