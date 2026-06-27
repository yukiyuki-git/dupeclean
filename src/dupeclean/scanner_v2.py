"""File deduplication file scanner v2 for DupeClean.

Enhanced file scanner with advanced features.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ScanResultV2:
    """Enhanced scan result."""

    root: Path
    files: list[FileInfo] = field(default_factory=list)
    scan_time: float = 0.0
    errors: list[str] = field(default_factory=list)
    skipped: int = 0

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def total_size_display(self) -> str:
        return format_size(self.total_size)


def scan_directory_v2(
    root: Path,
    follow_symlinks: bool = False,
    ignore_patterns: list[str] | None = None,
    max_depth: int = 50,
) -> ScanResultV2:
    """Scan a directory with enhanced features."""
    result = ScanResultV2(root=root)
    start = time.monotonic()
    patterns = ignore_patterns or []

    _walk_v2(root, 0, max_depth, follow_symlinks, patterns, result)
    result.scan_time = time.monotonic() - start
    return result


def _walk_v2(
    directory: Path,
    depth: int,
    max_depth: int,
    follow_symlinks: bool,
    patterns: list[str],
    result: ScanResultV2,
) -> None:
    """Recursively walk directory tree."""
    if depth > max_depth:
        return

    try:
        entries = list(os.scandir(directory))
    except (PermissionError, OSError):
        result.errors.append(f"Cannot read: {directory}")
        return

    for entry in entries:
        try:
            name = entry.name
            if name.startswith(".") or any(name == p for p in patterns):
                result.skipped += 1
                continue

            if entry.is_symlink() and not follow_symlinks:
                result.skipped += 1
                continue

            if entry.is_dir(follow_symlinks=follow_symlinks):
                _walk_v2(
                    Path(entry.path),
                    depth + 1,
                    max_depth,
                    follow_symlinks,
                    patterns,
                    result,
                )
            elif entry.is_file(follow_symlinks=follow_symlinks):
                fi = FileInfo.from_path(Path(entry.path), follow_symlinks)
                if fi:
                    result.files.append(fi)
        except (PermissionError, OSError):
            result.skipped += 1


def format_scan_result_v2(result: ScanResultV2) -> str:
    """Format scan result as text."""
    lines = [
        f"Scan Result: {result.root}",
        f"  Files: {result.file_count:,}",
        f"  Size: {result.total_size_display}",
        f"  Time: {result.scan_time:.2f}s",
    ]
    if result.errors:
        lines.append(f"  Errors: {len(result.errors)}")
    if result.skipped:
        lines.append(f"  Skipped: {result.skipped:,}")
    return "\n".join(lines)
