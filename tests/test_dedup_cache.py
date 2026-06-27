"""Tests for DupeClean dedup cache module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_cache import (
    DedupCache,
    format_cache_stats,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestDedupCache:
    def test_add_and_get(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a", group_id=0)
        assert cache.count == 1
        entry = cache.get(fi.path)
        assert entry is not None
        assert entry.hash_value == "hash_a"

    def test_get_nonexistent(self):
        cache = DedupCache()
        assert cache.get(Path("/nope")) is None

    def test_is_valid(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a")
        assert cache.is_valid(fi) is True

    def test_is_valid_size_changed(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a")
        fi_changed = _fi("/a.txt", 200, 1.0)
        assert cache.is_valid(fi_changed) is False

    def test_is_valid_mtime_changed(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a")
        fi_changed = _fi("/a.txt", 100, 2.0)
        assert cache.is_valid(fi_changed) is False

    def test_get_hash_valid(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a")
        assert cache.get_hash(fi) == "hash_a"

    def test_get_hash_invalid(self):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a")
        fi_changed = _fi("/a.txt", 200, 1.0)
        assert cache.get_hash(fi_changed) is None

    def test_save_and_load(self, tmp_path):
        cache = DedupCache()
        fi = _fi("/a.txt", 100, 1.0)
        cache.add(fi, "hash_a", group_id=0)

        path = tmp_path / "cache.json"
        cache.save(path)
        assert path.exists()

        loaded = DedupCache.load(path)
        assert loaded.count == 1
        assert loaded.get_hash(fi) == "hash_a"

    def test_load_nonexistent(self, tmp_path):
        cache = DedupCache.load(tmp_path / "nope")
        assert cache.count == 0

    def test_stats(self):
        cache = DedupCache()
        cache.add(_fi("/a"), "hash_a")
        stats = cache.stats()
        assert stats["entries"] == 1


class TestFormatCacheStats:
    def test_basic(self):
        cache = DedupCache()
        cache.add(_fi("/a"), "hash_a")
        text = format_cache_stats(cache)
        assert "1" in text

    def test_never_updated(self):
        cache = DedupCache()
        text = format_cache_stats(cache)
        assert "never" in text
