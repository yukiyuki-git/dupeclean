"""Tests for DupeClean finder v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.finder_v2 import (
    FinderResult,
    find_by_partial_hash,
    find_by_size_and_name,
    format_finder_result,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestFindBySizeAndName:
    def test_basic(self):
        files = [
            _fi("/a/photo.jpg", 1000),
            _fi("/b/photo.jpg", 1000),
            _fi("/c/other.txt", 1000),
        ]
        result = find_by_size_and_name(files)
        assert result.count >= 1

    def test_no_duplicates(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.py", 200),
        ]
        result = find_by_size_and_name(files)
        assert result.count == 0


class TestFindByPartialHash:
    def test_basic(self):
        files = [
            _fi("/a.txt", 100, "h1"),
            _fi("/b.txt", 100, "h1"),
            _fi("/c.txt", 200, "h2"),
        ]
        result = find_by_partial_hash(files)
        assert result.count == 1

    def test_no_hash(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        result = find_by_partial_hash(files)
        assert result.count == 0


class TestFinderResult:
    def test_total_duplicates(self):
        result = FinderResult()
        assert result.total_duplicates == 0

    def test_wasted_display(self):
        result = FinderResult()
        assert "B" in result.wasted_display


class TestFormatFinderResult:
    def test_basic(self):
        result = FinderResult(method="test", files_scanned=100)
        text = format_finder_result(result)
        assert "test" in text
