"""Tests for DupeClean file grouping module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.groups import (
    FileGroup,
    format_groups,
    group_by_age,
    group_by_directory,
    group_by_extension,
    group_by_size_range,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestGroupByExtension:
    def test_basic(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.txt", 200),
            _fi("/c.py", 300),
        ]
        groups = group_by_extension(files)
        assert len(groups) == 2
        txt = next(g for g in groups if g.key == ".txt")
        assert txt.count == 2

    def test_sorted_by_size(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.bin", 10000),
            _fi("/c.py", 500),
        ]
        groups = group_by_extension(files)
        assert groups[0].key == ".bin"  # Largest total


class TestGroupBySizeRange:
    def test_basic(self):
        files = [
            _fi("/a", 0),  # empty
            _fi("/b", 500),  # tiny
            _fi("/c", 50000),  # small
            _fi("/d", 500000),  # medium
            _fi("/e", 5000000),  # large
        ]
        groups = group_by_size_range(files)
        assert len(groups) == 5

    def test_custom_ranges(self):
        files = [_fi("/a", 500), _fi("/b", 5000)]
        ranges = [("small", 0, 1000), ("big", 1000, 10000)]
        groups = group_by_size_range(files, ranges)
        assert len(groups) == 2


class TestGroupByDirectory:
    def test_basic(self):
        files = [
            _fi("/a/file1.txt", 100),
            _fi("/a/file2.txt", 200),
            _fi("/b/file3.txt", 300),
        ]
        groups = group_by_directory(files)
        assert len(groups) == 2

    def test_sorted_by_size(self):
        files = [
            _fi("/small/a.txt", 100),
            _fi("/big/b.bin", 10000),
        ]
        groups = group_by_directory(files)
        # Largest directory should be first
        assert groups[0].total_size > groups[1].total_size


class TestGroupByAge:
    def test_basic(self):
        now = time.time()
        files = [
            _fi("/a", mtime=now - 3600),  # today
            _fi("/b", mtime=now - 86400 * 3),  # this week
            _fi("/c", mtime=now - 86400 * 15),  # this month
            _fi("/d", mtime=now - 86400 * 200),  # this year
            _fi("/e", mtime=now - 86400 * 400),  # older
        ]
        groups = group_by_age(files)
        assert len(groups) == 5


class TestFileGroup:
    def test_count(self):
        group = FileGroup(key="test", files=[_fi("/a"), _fi("/b")])
        assert group.count == 2

    def test_total_size(self):
        group = FileGroup(key="test", files=[_fi("/a", 100), _fi("/b", 200)])
        assert group.total_size == 300

    def test_size_display(self):
        group = FileGroup(key="test", files=[_fi("/a", 1024)])
        assert "B" in group.size_display


class TestFormatGroups:
    def test_empty(self):
        assert "No groups" in format_groups([])

    def test_with_groups(self):
        groups = [
            FileGroup(key=".txt", files=[_fi("/a", 100)]),
            FileGroup(key=".py", files=[_fi("/b", 200)]),
        ]
        text = format_groups(groups)
        assert ".txt" in text
        assert ".py" in text
