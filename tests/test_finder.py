"""Tests for DupeClean duplicate finder module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.finder import (
    FindResult,
    find_by_hash,
    find_by_size,
    format_find_result,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestFindBySize:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 200)]
        result = find_by_size(files)
        assert result.count == 1
        assert result.method == "size"

    def test_no_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        result = find_by_size(files)
        assert result.count == 0

    def test_sorted_by_waste(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 100),
            _fi("/c", 1000),
            _fi("/d", 1000),
            _fi("/e", 1000),
        ]
        result = find_by_size(files)
        assert result.groups[0].file_size == 1000


class TestFindByHash:
    def test_basic(self):
        files = [_fi("/a", 100, "h1"), _fi("/b", 100, "h1")]
        result = find_by_hash(files)
        assert result.count == 1

    def test_no_hash(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        result = find_by_hash(files)
        assert result.count == 0


class TestFindResult:
    def test_total_duplicates(self):
        result = FindResult()
        assert result.total_duplicates == 0

    def test_wasted_display(self):
        result = FindResult()
        # Add a group to give it wasted space
        from dupeclean.models import DuplicateGroup
        result.groups.append(DuplicateGroup(
            group_id=0, hash_value="abc", file_size=1024,
            files=[_fi("/a", 1024), _fi("/b", 1024)],
        ))
        assert "B" in result.wasted_display


class TestFormatFindResult:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        result = find_by_size(files)
        text = format_find_result(result)
        assert "size" in text
