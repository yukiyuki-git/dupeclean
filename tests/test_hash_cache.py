"""Tests for DupeClean hash cache module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.hash_cache import (
    HashCache,
    format_hash_cache_stats,
)


class TestHashCache:
    def test_put_and_get(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "hash_a")
        result = cache.get(Path("/a"), 100, 1.0)
        assert result == "hash_a"

    def test_get_invalid_size(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "hash_a")
        assert cache.get(Path("/a"), 200, 1.0) is None

    def test_get_invalid_mtime(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "hash_a")
        assert cache.get(Path("/a"), 100, 2.0) is None

    def test_get_nonexistent(self):
        cache = HashCache()
        assert cache.get(Path("/nope"), 100, 1.0) is None

    def test_invalidate(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "hash_a")
        cache.invalidate(Path("/a"))
        assert cache.get(Path("/a"), 100, 1.0) is None

    def test_count(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "h1")
        cache.put(Path("/b"), 200, 2.0, "h2")
        assert cache.count == 2

    def test_save_and_load(self, tmp_path):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "hash_a")
        path = tmp_path / "cache.json"
        cache.save(path)
        assert path.exists()

        loaded = HashCache.load(path)
        assert loaded.count == 1
        assert loaded.get(Path("/a"), 100, 1.0) == "hash_a"

    def test_load_nonexistent(self, tmp_path):
        cache = HashCache.load(tmp_path / "nope")
        assert cache.count == 0


class TestFormatHashCacheStats:
    def test_basic(self):
        cache = HashCache()
        cache.put(Path("/a"), 100, 1.0, "h")
        text = format_hash_cache_stats(cache)
        assert "1" in text
