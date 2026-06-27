"""Tests for DupeClean file indexer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.indexer import (
    FileIndex,
    build_index,
    format_index,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestFileIndex:
    def test_add(self):
        index = FileIndex()
        index.add(_fi("/a.txt", 100))
        assert index.total_files == 1

    def test_get_by_path(self):
        index = FileIndex()
        fi = _fi("/a.txt", 100)
        index.add(fi)
        assert index.get_by_path(Path("/a.txt")) is not None

    def test_get_by_size(self):
        index = FileIndex()
        index.add(_fi("/a", 100))
        index.add(_fi("/b", 100))
        index.add(_fi("/c", 200))
        assert len(index.get_by_size(100)) == 2

    def test_get_by_ext(self):
        index = FileIndex()
        index.add(_fi("/a.txt", 100))
        index.add(_fi("/b.py", 200))
        assert len(index.get_by_ext(".txt")) == 1

    def test_get_duplicates_by_size(self):
        index = FileIndex()
        index.add(_fi("/a", 100))
        index.add(_fi("/b", 100))
        index.add(_fi("/c", 200))
        dupes = index.get_duplicates_by_size()
        assert 100 in dupes
        assert 200 not in dupes

    def test_get_duplicates_by_hash(self):
        index = FileIndex()
        index.add(_fi("/a", 100, "h1"))
        index.add(_fi("/b", 100, "h1"))
        index.add(_fi("/c", 200, "h2"))
        dupes = index.get_duplicates_by_hash()
        assert "h1" in dupes
        assert "h2" not in dupes


class TestBuildIndex:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        index = build_index(files)
        assert index.total_files == 2


class TestFormatIndex:
    def test_basic(self):
        index = build_index([_fi("/a", 100), _fi("/b", 200)])
        text = format_index(index)
        assert "2" in text
