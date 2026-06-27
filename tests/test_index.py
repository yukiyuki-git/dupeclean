"""Tests for DupeClean index module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.index import (
    FileIndex,
    build_index,
    format_index_stats,
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
        fi = _fi("/a.txt", 100)
        index.add(fi)
        assert index.total_files == 1

    def test_by_size(self):
        index = FileIndex()
        index.add(_fi("/a", 100))
        index.add(_fi("/b", 100))
        index.add(_fi("/c", 200))
        assert len(index.by_size[100]) == 2
        assert len(index.by_size[200]) == 1

    def test_by_hash(self):
        index = FileIndex()
        index.add(_fi("/a", 100, "h1"))
        index.add(_fi("/b", 100, "h1"))
        index.add(_fi("/c", 200, "h2"))
        assert len(index.by_hash["h1"]) == 2

    def test_by_extension(self):
        index = FileIndex()
        index.add(_fi("/a.txt", 100))
        index.add(_fi("/b.txt", 200))
        index.add(_fi("/c.py", 300))
        assert len(index.by_extension[".txt"]) == 2
        assert len(index.by_extension[".py"]) == 1

    def test_total_size(self):
        index = FileIndex()
        index.add(_fi("/a", 100))
        index.add(_fi("/b", 200))
        assert index.total_size == 300

    def test_get_size_duplicates(self):
        index = FileIndex()
        index.add(_fi("/a", 100))
        index.add(_fi("/b", 100))
        index.add(_fi("/c", 200))
        dupes = index.get_size_duplicates()
        assert 100 in dupes
        assert 200 not in dupes

    def test_get_hash_duplicates(self):
        index = FileIndex()
        index.add(_fi("/a", 100, "h1"))
        index.add(_fi("/b", 100, "h1"))
        index.add(_fi("/c", 200, "h2"))
        dupes = index.get_hash_duplicates()
        assert "h1" in dupes
        assert "h2" not in dupes

    def test_get_by_extension(self):
        index = FileIndex()
        index.add(_fi("/a.txt", 100))
        assert len(index.get_by_extension(".txt")) == 1
        assert len(index.get_by_extension(".py")) == 0


class TestBuildIndex:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        index = build_index(files)
        assert index.total_files == 2

    def test_empty(self):
        index = build_index([])
        assert index.total_files == 0


class TestFormatIndexStats:
    def test_basic(self):
        index = build_index([_fi("/a", 100), _fi("/b", 100)])
        text = format_index_stats(index)
        assert "2" in text
