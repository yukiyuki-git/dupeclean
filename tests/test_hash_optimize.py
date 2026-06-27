"""Tests for DupeClean hash optimization module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.hash_optimize import (
    HashStats,
    batch_hash_files,
    optimize_hash_order,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestBatchHashFiles:
    def test_basic(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.write_text("world")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        results = batch_hash_files(files)
        assert len(results) == 2

    def test_same_content_same_hash(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        results = batch_hash_files(files)
        hashes = list(results.values())
        assert hashes[0] == hashes[1]

    def test_with_cache(self, tmp_path):
        a = tmp_path / "a.txt"
        a.write_text("hello")
        files = [FileInfo.from_path(a)]
        files = [f for f in files if f is not None]
        cache: dict[str, str] = {}
        results = batch_hash_files(files, cache=cache)
        assert len(cache) == 1
        # Second call should use cache
        results2 = batch_hash_files(files, cache=cache)
        assert results == results2

    def test_empty_list(self):
        results = batch_hash_files([])
        assert len(results) == 0


class TestHashStats:
    def test_throughput(self):
        stats = HashStats(bytes_hashed=1048576, duration=1.0)
        assert abs(stats.throughput_mbps - 1.0) < 0.01

    def test_zero_duration(self):
        stats = HashStats(bytes_hashed=1024, duration=0.0)
        assert stats.throughput_mbps == 0.0


class TestOptimizeHashOrder:
    def test_small_first(self):
        files = [
            _fi("/big", 10000),
            _fi("/small", 100),
            _fi("/medium", 1000),
        ]
        ordered = optimize_hash_order(files)
        assert ordered[0].size == 100
        assert ordered[-1].size == 10000
