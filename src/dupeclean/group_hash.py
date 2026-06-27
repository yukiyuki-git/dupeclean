"""File deduplication group hash module for DupeClean.

Hash files within groups for content comparison.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class HashResult:
    """Result of hashing a file."""

    path: str
    hash_value: str
    algorithm: str
    size: int = 0


@dataclass
class GroupHashResult:
    """Result of hashing files in a group."""

    results: list[HashResult] = field(default_factory=list)
    algorithm: str = "sha256"

    @property
    def count(self) -> int:
        return len(self.results)

    def get_hash(self, path: str) -> str | None:
        for r in self.results:
            if r.path == path:
                return r.hash_value
        return None


def hash_group_files(
    files: list[FileInfo],
    algorithm: str = "sha256",
    sample_size: int = 0,
) -> GroupHashResult:
    """Hash all files in a group.

    Args:
        files: Files to hash.
        algorithm: Hash algorithm.
        sample_size: Bytes to read (0 = entire file).

    Returns:
        GroupHashResult with hashes.
    """
    result = GroupHashResult(algorithm=algorithm)

    for fi in files:
        h = _hash_file(fi.path, algorithm, sample_size)
        if h:
            result.results.append(
                HashResult(
                    path=str(fi.path),
                    hash_value=h,
                    algorithm=algorithm,
                    size=fi.size,
                )
            )

    return result


def _hash_file(
    filepath: Path,
    algorithm: str,
    sample_size: int = 0,
) -> str | None:
    """Hash a file."""
    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            if sample_size > 0:
                data = f.read(sample_size)
                h.update(data)
            else:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
        return h.hexdigest()
    except (OSError, ValueError):
        return None


def find_hash_conflicts(
    result: GroupHashResult,
) -> dict[str, list[str]]:
    """Find files with the same hash."""
    groups: dict[str, list[str]] = {}
    for r in result.results:
        groups.setdefault(r.hash_value, []).append(r.path)
    return {h: paths for h, paths in groups.items() if len(paths) > 1}


def format_hash_result(result: GroupHashResult) -> str:
    """Format hash result as text."""
    conflicts = find_hash_conflicts(result)
    return f"Hashed: {result.count} files ({result.algorithm}), {len(conflicts)} conflicts found"
