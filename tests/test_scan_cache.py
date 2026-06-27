"""Tests for DupeClean scan cache module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.scan_cache import (
    ScanCache,
    format_scan_cache,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestScanCache:
    def test_add(self):
        cache = ScanCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi)
        assert cache.count == 1

    def test_get(self):
        cache = ScanCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi)
        entry = cache.get(fi.path)
        assert entry is not None
        assert entry.size == 100

    def test_is_valid(self):
        cache = ScanCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi)
        assert cache.is_valid(fi) is True

    def test_is_valid_changed(self):
        cache = ScanCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi)
        fi_changed = _fi("/a.txt", 200, 1.0)
        assert cache.is_valid(fi_changed) is False

    def test_get_unchanged(self):
        cache = ScanCache()
        files = [_fi("/a", 100, 1.0), _fi("/b", 200, 2.0)]
        for f in files:
            cache.add(f)
        unchanged = cache.get_unchanged(files)
        assert len(unchanged) == 2

    def test_get_changed(self):
        cache = ScanCache()
        fi = _fi("/a", 100, 1.0)
        cache.add(fi)
        fi_changed = _fi("/a", 200, 2.0)
        changed = cache.get_changed([fi_changed])
        assert len(changed) == 1

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "cache.json"
        cache = ScanCache()
        cache.add(_fi("/a", 100, 1.0))
        cache.save(path)
        assert path.exists()

        loaded = ScanCache.load(path)
        assert loaded.count == 1

    def test_load_nonexistent(self, tmp_path):
        cache = ScanCache.load(tmp_path / "nope")
        assert cache.count == 0


class TestFormatScanCache:
    def test_empty(self):
        cache = ScanCache()
        assert "never" in format_scan_cache(cache)

    def test_with_entries(self):
        cache = ScanCache()
        cache.add(_fi("/a", 100))
        cache.last_scan = time.time()
        text = format_scan_cache(cache)
        assert "1" in text
