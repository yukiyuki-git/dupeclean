"""Tests for DupeClean rate limiter module."""

from __future__ import annotations

from dupeclean.throttle import (
    RateLimiter,
    ThrottledReader,
    create_limiter,
)


class TestRateLimiter:
    def test_basic_acquire(self):
        limiter = RateLimiter(max_ops_per_second=1000, burst_size=10)
        wait = limiter.acquire()
        assert wait == 0.0

    def test_burst(self):
        limiter = RateLimiter(max_ops_per_second=10, burst_size=5)
        # Should allow burst without waiting
        for _ in range(5):
            limiter.acquire()
        assert limiter.total_operations == 5

    def test_available_tokens(self):
        limiter = RateLimiter(max_ops_per_second=100, burst_size=10)
        assert limiter.available_tokens == 10.0

    def test_total_operations(self):
        limiter = RateLimiter(max_ops_per_second=1000, burst_size=10)
        for _ in range(5):
            limiter.acquire()
        assert limiter.total_operations == 5


class TestCreateLimiter:
    def test_basic(self):
        limiter = create_limiter(100, 10)
        assert limiter.max_ops_per_second == 100
        assert limiter.burst_size == 10


class TestThrottledReader:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        with ThrottledReader(f) as reader:
            data = reader.read(5)
            assert data == b"hello"

    def test_custom_limiter(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"test data")
        limiter = create_limiter(1000, 100)
        with ThrottledReader(f, limiter) as reader:
            data = reader.read()
            assert data == b"test data"
