"""Tests for DupeClean file statistics module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.statistics import (
    compute_extension_stats,
    compute_stats,
    format_extension_stats,
    format_file_stats,
)


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestComputeStats:
    def test_basic(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 200),
            _fi("/c", 300),
        ]
        stats = compute_stats(files)
        assert stats.count == 3
        assert stats.total_size == 600
        assert stats.min_size == 100
        assert stats.max_size == 300
        assert stats.mean_size == 200

    def test_empty(self):
        stats = compute_stats([])
        assert stats.count == 0
        assert stats.total_size == 0

    def test_single_file(self):
        stats = compute_stats([_fi("/a", 500)])
        assert stats.count == 1
        assert stats.total_size == 500
        assert stats.min_size == 500
        assert stats.max_size == 500

    def test_percentiles(self):
        files = [_fi(f"/f{i}", (i + 1) * 100) for i in range(100)]
        stats = compute_stats(files)
        assert stats.p25_size > 0
        assert stats.p75_size > stats.p25_size
        assert stats.p95_size > stats.p75_size


class TestFileStats:
    def test_total_display(self):
        stats = compute_stats([_fi("/a", 1024)])
        assert "B" in stats.total_display

    def test_mean_display(self):
        stats = compute_stats([_fi("/a", 1024)])
        assert "B" in stats.mean_display


class TestComputeExtensionStats:
    def test_basic(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.txt", 200),
            _fi("/c.py", 300),
        ]
        ext_stats = compute_extension_stats(files)
        assert ".txt" in ext_stats
        assert ".py" in ext_stats
        assert ext_stats[".txt"].count == 2


class TestFormatFileStats:
    def test_empty(self):
        assert "No files" in format_file_stats(compute_stats([]))

    def test_with_files(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        text = format_file_stats(compute_stats(files))
        assert "2" in text


class TestFormatExtensionStats:
    def test_basic(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.py", 200),
        ]
        ext_stats = compute_extension_stats(files)
        text = format_extension_stats(ext_stats)
        assert ".txt" in text
        assert ".py" in text
