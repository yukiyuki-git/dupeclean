"""Tests for DupeClean SQLite scan cache."""

from __future__ import annotations

import time

import pytest

from dupeclean.cache import ScanCache
from dupeclean.models import FileInfo


@pytest.fixture
def cache(tmp_path):
    """Create a temporary scan cache."""
    db_path = tmp_path / "test_cache.db"
    with ScanCache(db_path) as c:
        yield c


@pytest.fixture
def sample_files(tmp_path):
    """Create sample files."""
    files = []
    for name, content in [
        ("a.txt", b"hello"),
        ("b.txt", b"world"),
        ("c.bin", b"\x00" * 1024),
    ]:
        p = tmp_path / name
        p.write_bytes(content)
        fi = FileInfo.from_path(p)
        if fi:
            fi.quick_hash = f"hash_{name}"
            files.append(fi)
    return files


class TestScanCache:
    def test_put_and_get(self, cache, sample_files):
        fi = sample_files[0]
        cache.put(fi)
        entry = cache.get(fi.path)

        assert entry is not None
        assert entry.size == fi.size
        assert entry.mtime == fi.mtime
        assert entry.quick_hash == fi.quick_hash

    def test_get_nonexistent(self, cache, tmp_path):
        entry = cache.get(tmp_path / "nope.txt")
        assert entry is None

    def test_put_overwrites(self, cache, sample_files):
        fi = sample_files[0]
        cache.put(fi)
        fi.quick_hash = "updated_hash"
        cache.put(fi)

        entry = cache.get(fi.path)
        assert entry is not None
        assert entry.quick_hash == "updated_hash"

    def test_is_cached_match(self, cache, sample_files):
        fi = sample_files[0]
        cache.put(fi)
        assert cache.is_cached(fi.path, fi.size, fi.mtime) is True

    def test_is_cached_size_mismatch(self, cache, sample_files):
        fi = sample_files[0]
        cache.put(fi)
        assert cache.is_cached(fi.path, fi.size + 1, fi.mtime) is False

    def test_is_cached_mtime_mismatch(self, cache, sample_files):
        fi = sample_files[0]
        cache.put(fi)
        assert cache.is_cached(fi.path, fi.size, fi.mtime + 1) is False

    def test_is_cached_unknown_file(self, cache, tmp_path):
        assert cache.is_cached(tmp_path / "nope", 100, 1.0) is False

    def test_put_batch(self, cache, sample_files):
        cache.put_batch(sample_files)
        for fi in sample_files:
            entry = cache.get(fi.path)
            assert entry is not None

    def test_get_uncached(self, cache, sample_files, tmp_path):
        # Cache all sample files
        cache.put_batch(sample_files)

        # Add a new uncached file
        new_file = tmp_path / "new.txt"
        new_file.write_bytes(b"new content")
        fi_new = FileInfo.from_path(new_file)
        assert fi_new is not None
        all_files = [*sample_files, fi_new]

        uncached = cache.get_uncached(all_files)
        # Only new file should be uncached
        assert len(uncached) == 1
        assert uncached[0].path == new_file

    def test_apply_cached_hashes(self, cache, sample_files):
        cache.put_batch(sample_files)

        # Clear hashes on files
        for fi in sample_files:
            fi.quick_hash = None

        hits = cache.apply_cached_hashes(sample_files)
        assert hits == len(sample_files)

        # Hashes should be restored
        for fi in sample_files:
            assert fi.quick_hash is not None

    def test_record_and_get_scan_history(self, cache):
        cache.record_scan("/test", 100, 1024, 5, 512)
        time.sleep(0.01)  # Ensure different timestamps
        cache.record_scan("/test", 200, 2048, 10, 1024)

        history = cache.get_scan_history("/test")
        assert len(history) == 2
        # Most recent first (200 files)
        assert history[0]["files"] == 200
        assert history[1]["files"] == 100

    def test_get_all_history(self, cache):
        cache.record_scan("/a", 10, 100, 1, 50)
        cache.record_scan("/b", 20, 200, 2, 100)

        history = cache.get_scan_history()
        assert len(history) == 2

    def test_purge_old(self, cache, sample_files):
        cache.put_batch(sample_files)

        # All entries are fresh, nothing should be purged
        purged = cache.purge_old(max_age_days=30)
        assert purged == 0

    def test_clear(self, cache, sample_files):
        cache.put_batch(sample_files)
        cache.record_scan("/test", 10, 100, 1, 50)

        cache.clear()
        stats = cache.stats()
        assert stats["cached_files"] == 0
        assert stats["scan_history"] == 0

    def test_stats(self, cache, sample_files):
        cache.put_batch(sample_files)
        stats = cache.stats()

        assert stats["cached_files"] == len(sample_files)
        assert stats["scan_history"] == 0
        assert stats["db_size_bytes"] > 0

    def test_context_manager(self, tmp_path):
        db_path = tmp_path / "ctx_test.db"
        with ScanCache(db_path) as cache:
            cache.record_scan("/test", 10, 100, 1, 50)
            assert cache.stats()["scan_history"] == 1
        # Connection should be closed now

    def test_empty_cache_stats(self, cache):
        stats = cache.stats()
        assert stats["cached_files"] == 0
        assert stats["scan_history"] == 0
