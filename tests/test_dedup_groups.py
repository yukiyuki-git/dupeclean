"""Tests for DupeClean dedup grouping module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_groups import (
    DedupGroup,
    format_dedup_groups,
    group_by_hash,
    group_by_name_pattern,
    group_by_size,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestGroupBySize:
    def test_basic(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 100),
            _fi("/c", 200),
            _fi("/d", 200),
            _fi("/e", 200),
        ]
        groups = group_by_size(files)
        assert len(groups) == 2

    def test_no_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        groups = group_by_size(files)
        assert len(groups) == 0

    def test_sorted_by_waste(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 100),
            _fi("/c", 1000),
            _fi("/d", 1000),
            _fi("/e", 1000),
        ]
        groups = group_by_size(files)
        assert groups[0].file_size == 1000


class TestGroupByHash:
    def test_basic(self):
        files = [
            _fi("/a", 100, "h1"),
            _fi("/b", 100, "h1"),
            _fi("/c", 200, "h2"),
            _fi("/d", 200, "h2"),
        ]
        groups = group_by_hash(files)
        assert len(groups) == 2

    def test_no_hash(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        groups = group_by_hash(files)
        assert len(groups) == 0


class TestGroupByNamePattern:
    def test_copy_pattern(self):
        files = [
            _fi("/photo.jpg", 100),
            _fi("/photo (1).jpg", 100),
            _fi("/photo (2).jpg", 100),
        ]
        groups = group_by_name_pattern(files)
        assert len(groups) >= 1


class TestDedupGroup:
    def test_count(self):
        g = DedupGroup(key="test", method="size", files=[_fi("/a"), _fi("/b")])
        assert g.count == 2

    def test_wasted_space(self):
        g = DedupGroup(
            key="test",
            method="size",
            files=[_fi("/a", 1000), _fi("/b", 1000), _fi("/c", 1000)],
        )
        assert g.wasted_space == 2000

    def test_wasted_display(self):
        g = DedupGroup(key="test", method="size", files=[_fi("/a", 1024), _fi("/b", 1024)])
        assert "B" in g.wasted_display


class TestFormatDedupGroups:
    def test_empty(self):
        assert "No duplicate" in format_dedup_groups([])

    def test_with_groups(self):
        groups = [
            DedupGroup(
                key="100",
                method="size",
                files=[_fi("/a", 100), _fi("/b", 100)],
            )
        ]
        text = format_dedup_groups(groups)
        assert "size" in text
