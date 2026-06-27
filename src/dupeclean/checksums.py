"""Checksum verification module for DupeClean.

Generate and verify file checksums in standard formats
compatible with sha256sum, md5sum, etc.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChecksumEntry:
    """A single checksum entry."""

    hash_value: str
    path: Path
    algorithm: str


def generate_checksum(
    filepath: Path,
    algorithm: str = "sha256",
) -> str | None:
    """Generate checksum for a single file.

    Args:
        filepath: Path to file.
        algorithm: Hash algorithm (sha256, md5, sha1).

    Returns:
        Hex digest string, or None if file cannot be read.
    """
    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def generate_manifest(
    files: list[Path],
    algorithm: str = "sha256",
    root: Path | None = None,
) -> list[ChecksumEntry]:
    """Generate checksums for multiple files.

    Args:
        files: List of file paths.
        algorithm: Hash algorithm.
        root: Root directory for relative paths.

    Returns:
        List of ChecksumEntry.
    """
    entries: list[ChecksumEntry] = []
    for filepath in files:
        hash_val = generate_checksum(filepath, algorithm)
        if hash_val:
            entries.append(
                ChecksumEntry(
                    hash_value=hash_val,
                    path=filepath,
                    algorithm=algorithm,
                )
            )
    return entries


def format_manifest(
    entries: list[ChecksumEntry],
    root: Path | None = None,
    relative: bool = True,
) -> str:
    """Format checksum entries in sha256sum-compatible format.

    Output: <hash>  <path>
    """
    lines = []
    for entry in entries:
        if relative and root:
            try:
                display_path = entry.path.relative_to(root)
            except ValueError:
                display_path = entry.path
        else:
            display_path = entry.path
        lines.append(f"{entry.hash_value}  {display_path}")
    return "\n".join(lines)


def parse_manifest(
    content: str,
) -> list[ChecksumEntry]:
    """Parse a sha256sum-compatible manifest file.

    Format: <hash>  <path>
    """
    entries: list[ChecksumEntry] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) == 2:
            hash_val, path_str = parts
            # Detect algorithm from hash length
            algo = _guess_algorithm(hash_val)
            entries.append(
                ChecksumEntry(
                    hash_value=hash_val,
                    path=Path(path_str),
                    algorithm=algo,
                )
            )
    return entries


def verify_manifest(
    entries: list[ChecksumEntry],
) -> list[tuple[ChecksumEntry, bool]]:
    """Verify files against their checksums.

    Returns list of (entry, is_valid) tuples.
    """
    results: list[tuple[ChecksumEntry, bool]] = []
    for entry in entries:
        current_hash = generate_checksum(entry.path, entry.algorithm)
        is_valid = current_hash == entry.hash_value
        results.append((entry, is_valid))
    return results


def _guess_algorithm(hash_value: str) -> str:
    """Guess algorithm from hash length."""
    length = len(hash_value)
    if length == 32:
        return "md5"
    if length == 40:
        return "sha1"
    if length == 64:
        return "sha256"
    if length == 128:
        return "sha512"
    return "sha256"  # default
