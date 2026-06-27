"""File integrity checker for DupeClean.

Verify file integrity using multiple hash algorithms
and detect bit rot or corruption.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IntegrityResult:
    """Result of an integrity check."""

    path: Path
    algorithm: str
    hash_value: str
    file_size: int
    is_valid: bool = True
    error: str = ""


def compute_hash(
    filepath: Path,
    algorithm: str = "sha256",
) -> IntegrityResult | None:
    """Compute hash of a file."""
    try:
        size = filepath.stat().st_size
    except OSError:
        return None

    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return IntegrityResult(
            path=filepath,
            algorithm=algorithm,
            hash_value=h.hexdigest(),
            file_size=size,
        )
    except (OSError, ValueError) as e:
        return IntegrityResult(
            path=filepath,
            algorithm=algorithm,
            hash_value="",
            file_size=size,
            is_valid=False,
            error=str(e),
        )


def verify_hash(
    filepath: Path,
    expected_hash: str,
    algorithm: str = "sha256",
) -> IntegrityResult | None:
    """Verify a file's hash matches expected value."""
    result = compute_hash(filepath, algorithm)
    if result is None:
        return None
    result.is_valid = result.hash_value == expected_hash
    if not result.is_valid:
        result.error = "Hash mismatch"
    return result


def compute_multi_hash(
    filepath: Path,
    algorithms: list[str] | None = None,
) -> dict[str, IntegrityResult]:
    """Compute multiple hashes for a file."""
    if algorithms is None:
        algorithms = ["md5", "sha1", "sha256"]

    results = {}
    for algo in algorithms:
        result = compute_hash(filepath, algo)
        if result:
            results[algo] = result
    return results


def check_bit_rot(
    filepath: Path,
    known_hash: str,
    algorithm: str = "sha256",
) -> bool:
    """Check if a file has bit rot (hash mismatch).

    Returns True if file is OK, False if corrupted.
    """
    result = verify_hash(filepath, known_hash, algorithm)
    return result is not None and result.is_valid


def format_integrity_result(result: IntegrityResult) -> str:
    """Format integrity result as text."""
    status = "OK" if result.is_valid else "FAILED"
    return (
        f"[{status}] {result.path.name}: "
        f"{result.algorithm}={result.hash_value[:16]}... "
        f"({result.file_size:,} bytes)"
    )
