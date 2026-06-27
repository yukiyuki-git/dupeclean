"""File hashing utilities for DupeClean.

Additional hashing utilities beyond the basic hasher.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HashResult:
    """Result of a hash computation."""

    algorithm: str
    hash_value: str
    file_size: int
    duration: float = 0.0

    @property
    def short_hash(self) -> str:
        """Return first 16 chars of hash."""
        return self.hash_value[:16]


def hash_file_quick(filepath: Path, size: int = 4096) -> HashResult | None:
    """Hash first N bytes of a file."""
    try:
        file_size = filepath.stat().st_size
    except OSError:
        return None

    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            data = f.read(size)
            h.update(data)
        return HashResult(
            algorithm="sha256_quick",
            hash_value=h.hexdigest(),
            file_size=file_size,
        )
    except OSError:
        return None


def hash_file_full(filepath: Path) -> HashResult | None:
    """Hash entire file."""
    import time

    try:
        file_size = filepath.stat().st_size
    except OSError:
        return None

    start = time.monotonic()
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        duration = time.monotonic() - start
        return HashResult(
            algorithm="sha256",
            hash_value=h.hexdigest(),
            file_size=file_size,
            duration=duration,
        )
    except OSError:
        return None


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    """Hash raw data."""
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def format_hash_result(result: HashResult) -> str:
    """Format hash result as text."""
    return (
        f"{result.algorithm}: {result.hash_value}\n"
        f"  Size: {result.file_size:,} bytes\n"
        f"  Short: {result.short_hash}..."
    )
