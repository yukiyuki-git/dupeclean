"""Tests for DupeClean file filter module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.filters import (
    apply_filter,
    by_extension,
    by_max_age,
    by_max_size,
    by_min_age,
    by_min_size,
    by_name,
    by_name_regex,
    filter_summary,
    is_empty,
    is_symlink,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestFileFilter:
    def test_and(self):
        f1 = by_extension("txt")
        f2 = by_min_size(50)
        combined = f1 & f2
        assert combined(_fi("/a.txt", 100)) is True
        assert combined(_fi("/a.txt", 10)) is False
        assert combined(_fi("/a.py", 100)) is False

    def test_or(self):
        f1 = by_extension("txt")
        f2 = by_extension("py")
        combined = f1 | f2
        assert combined(_fi("/a.txt", 100)) is True
        assert combined(_fi("/a.py", 100)) is True
        assert combined(_fi("/a.jpg", 100)) is False

    def test_invert(self):
        f = by_extension("txt")
        inverted = ~f
        assert inverted(_fi("/a.txt", 100)) is False
        assert inverted(_fi("/a.py", 100)) is True


class TestByExtension:
    def test_basic(self):
        f = by_extension("txt")
        assert f(_fi("/a.txt")) is True
        assert f(_fi("/a.py")) is False

    def test_multiple(self):
        f = by_extension("txt", "md", "rst")
        assert f(_fi("/a.txt")) is True
        assert f(_fi("/a.md")) is True
        assert f(_fi("/a.py")) is False

    def test_case_insensitive(self):
        f = by_extension("TXT")
        assert f(_fi("/a.txt")) is True
        assert f(_fi("/a.TXT")) is True


class TestByName:
    def test_glob(self):
        f = by_name("*.txt")
        assert f(_fi("/test/a.txt")) is True
        assert f(_fi("/test/a.py")) is False

    def test_specific(self):
        f = by_name("README.md")
        assert f(_fi("/test/README.md")) is True


class TestByNameRegex:
    def test_basic(self):
        f = by_name_regex(r"photo_\d+")
        assert f(_fi("/test/photo_001.jpg")) is True
        assert f(_fi("/test/image.jpg")) is False


class TestBySize:
    def test_min_size(self):
        f = by_min_size(1000)
        assert f(_fi("/a", 2000)) is True
        assert f(_fi("/a", 500)) is False

    def test_max_size(self):
        f = by_max_size(1000)
        assert f(_fi("/a", 500)) is True
        assert f(_fi("/a", 2000)) is False


class TestByAge:
    def test_min_age(self):
        f = by_min_age(30)  # Older than 30 days
        old_time = time.time() - (40 * 86400)
        new_time = time.time() - (10 * 86400)
        assert f(_fi("/a", mtime=old_time)) is True
        assert f(_fi("/a", mtime=new_time)) is False

    def test_max_age(self):
        f = by_max_age(30)  # Newer than 30 days
        old_time = time.time() - (40 * 86400)
        new_time = time.time() - (10 * 86400)
        assert f(_fi("/a", mtime=new_time)) is True
        assert f(_fi("/a", mtime=old_time)) is False


class TestSpecialFilters:
    def test_is_empty(self):
        f = is_empty()
        assert f(_fi("/a", 0)) is True
        assert f(_fi("/a", 100)) is False

    def test_is_symlink(self):
        f = is_symlink()
        fi = _fi("/a")
        fi.is_symlink = True
        assert f(fi) is True
        assert f(_fi("/b")) is False


class TestApplyFilter:
    def test_basic(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.py", 200),
            _fi("/c.txt", 300),
        ]
        result = apply_filter(files, by_extension("txt"))
        assert len(result) == 2


class TestFilterSummary:
    def test_basic(self):
        text = filter_summary(100, 25, "txt")
        assert "25" in text
        assert "25.0%" in text
