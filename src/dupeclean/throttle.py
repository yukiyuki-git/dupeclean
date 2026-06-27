"""File rate limiter for DupeClean.

Control I/O rate to prevent overwhelming the system.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RateLimiter:
    """Token bucket rate limiter for I/O operations."""
    max_ops_per_second: float = 100.0
    burst_size: int = 10
    _tokens: float = 0.0
    _last_refill: float = 0.0
    _total_ops: int = 0

    def __post_init__(self) -> None:
        self._tokens = float(self.burst_size)
        self._last_refill = time.monotonic()

    def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, waiting if necessary.

        Returns:
            Seconds waited.
        """
        waited = 0.0
        while self._tokens < tokens:
            self._refill()
            if self._tokens < tokens:
                sleep_time = (tokens - self._tokens) / self.max_ops_per_second
                time.sleep(sleep_time)
                waited += sleep_time
                self._refill()
        self._tokens -= tokens
        self._total_ops += 1
        return waited

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            float(self.burst_size),
            self._tokens + elapsed * self.max_ops_per_second,
        )
        self._last_refill = now

    @property
    def available_tokens(self) -> float:
        self._refill()
        return self._tokens

    @property
    def total_operations(self) -> int:
        return self._total_ops


def create_limiter(
    ops_per_second: float = 100.0, burst: int = 10
) -> RateLimiter:
    """Create a rate limiter."""
    return RateLimiter(
        max_ops_per_second=ops_per_second,
        burst_size=burst,
    )


class ThrottledReader:
    """Rate-limited file reader."""

    def __init__(
        self, filepath: Path, limiter: RateLimiter | None = None
    ) -> None:
        self.filepath = filepath
        self.limiter = limiter or create_limiter(1000, 100)
        self._file = None

    def __enter__(self) -> ThrottledReader:
        self._file = open(self.filepath, "rb")
        return self

    def __exit__(self, *args) -> None:
        if self._file:
            self._file.close()

    def read(self, size: int = 8192) -> bytes:
        """Read with rate limiting."""
        self.limiter.acquire()
        if self._file:
            return self._file.read(size)
        return b""
