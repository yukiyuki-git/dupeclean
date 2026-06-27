"""File deduplication scanner module for DupeClean.

Specialized scanner for finding duplicate files.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ScanResult:
    """Result of a dedup scan."""

    root: Path
    files: list[FileInfo] = field(default_factory=list)
    scan_time: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def total_size_display(self) -> str:
        return format_size(self.total_size)


def scan_for_duplicates(
    root: Path,
    follow_symlinks: bool = False,
    ignore_patterns: list[str] | None = None,
) -> ScanResult:
    """Scan a directory tree for potential duplicates.

    Args:
        root: Root directory to scan.
        follow_symlinks: Whether to follow symlinks.
        ignore_patterns: Patterns to ignore.

    Returns:
        ScanResult with all files found.
    """
    result = ScanResult(root=root)
    start = time.monotonic()
    patterns = ignore_patterns or []

    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        # Filter ignored directories
        dirnames[:] = [
            d for d in dirnames if not any(d == p or d.startswith(".") for p in patterns)
        ]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            try:
                if not follow_symlinks and filepath.is_symlink():
                    continue
                fi = FileInfo.from_path(filepath, follow_symlinks)
                if fi:
                    result.files.append(fi)
            except (OSError, PermissionError) as e:
                result.errors.append(str(e))

    result.scan_time = time.monotonic() - start
    return result


def format_scan_result(result: ScanResult) -> str:
    """Format scan result as text."""
    lines = [
        f"Scan Result: {result.root}",
        f"  Files: {result.file_count:,}",
        f"  Size: {result.total_size_display}",
        f"  Time: {result.scan_time:.2f}s",
    ]
    if result.errors:
        lines.append(f"  Errors: {len(result.errors)}")
    return "\n".join(lines)
