"""File deduplication hashing optimization for DupeClean.

Optimized hashing strategies for better performance.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo


@dataclass
class HashStats:
    """Statistics for hashing operations."""
    files_hashed: int = 0
    bytes_hashed: int = 0
    duration: float = 0.0
    cache_hits: int = 0

    @property
    def throughput_mbps(self) -> float:
        if self.duration <= 0:
            return 0.0
        return (self.bytes_hashed / 1048576) / self.duration


def batch_hash_files(
    files: list[FileInfo],
    algorithm: str = "xxhash",
    chunk_size: int = 4096,
    cache: dict[str, str] | None = None,
) -> dict[str, str]:
    """Hash multiple files efficiently.

    Args:
        files: Files to hash.
        algorithm: Hash algorithm.
        chunk_size: Bytes to read for quick hash.
        cache: Optional hash cache for skip detection.

    Returns:
        Dict mapping file path to hash.
    """

    results: dict[str, str] = {}

    for fi in files:
        path_str = str(fi.path)

        # Check cache
        if cache and path_str in cache:
            results[path_str] = cache[path_str]
            continue

        # Compute hash
        h = _hash_file(fi.path, algorithm, chunk_size)
        if h:
            results[path_str] = h
            if cache is not None:
                cache[path_str] = h

    return results


def _hash_file(
    filepath: Path,
    algorithm: str,
    max_bytes: int = 0,
) -> str | None:
    """Hash a file with optional size limit."""
    try:
        h = _create_hasher(algorithm)
        with open(filepath, "rb") as f:
            bytes_read = 0
            while True:
                if max_bytes > 0:
                    remaining = max_bytes - bytes_read
                    if remaining <= 0:
                        break
                    chunk_size = min(65536, remaining)
                else:
                    chunk_size = 65536
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
                bytes_read += len(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _create_hasher(algorithm: str):
    """Create a hash object."""
    if algorithm == "xxhash":
        try:
            import xxhash
            return xxhash.xxh3_128()
        except ImportError:
            pass
    try:
        return hashlib.new(algorithm)
    except ValueError:
        return hashlib.md5()


def optimize_hash_order(files: list[FileInfo]) -> list[FileInfo]:
    """Optimize file order for hashing (small files first).

    Small files hash faster and can quickly eliminate
    non-duplicates before processing large files.
    """
    return sorted(files, key=lambda f: f.size)
