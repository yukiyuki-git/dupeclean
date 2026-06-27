"""Tests for DupeClean file stats module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.file_stats import (
    FileStatsV2,
    compute_file_stats,
    format_file_stats_v2,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestComputeFileStats:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 200), _fi("/c", 300)]
        stats = compute_file_stats(files)
        assert stats.total_files == 3
        assert stats.total_size == 600
        assert stats.min_size == 100
        assert stats.max_size == 300
        assert stats.avg_size == 200

    def test_empty(self):
        stats = compute_file_stats([])
        assert stats.total_files == 0

    def test_single_file(self):
        stats = compute_file_stats([_fi("/a", 500)])
        assert stats.total_files == 1
        assert stats.total_size == 500

    def test_percentiles(self):
        files = [_fi(f"/f{i}", (i + 1) * 100) for i in range(100)]
        stats = compute_file_stats(files)
        assert stats.p25_size > 0
        assert stats.p75_size > stats.p25_size


class TestFileStatsV2:
    def test_total_display(self):
        stats = compute_file_stats([_fi("/a", 1024)])
        assert "B" in stats.total_display

    def test_avg_display(self):
        stats = compute_file_stats([_fi("/a", 1024)])
        assert "B" in stats.avg_display


class TestFormatFileStatsV2:
    def test_empty(self):
        assert "No files" in format_file_stats_v2(FileStatsV2())

    def test_with_files(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        text = format_file_stats_v2(compute_file_stats(files))
        assert "2" in text
