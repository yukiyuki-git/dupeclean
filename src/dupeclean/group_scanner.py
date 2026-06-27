"""File deduplication group scanner for DupeClean.

Scan directories for potential duplicate groups.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ScanConfig:
    """Configuration for group scanning."""

    follow_symlinks: bool = False
    skip_hidden: bool = True
    max_depth: int = 50
    ignore_patterns: list[str] = field(
        default_factory=lambda: [".git", "node_modules", "__pycache__"]
    )


@dataclass
class ScanResult:
    """Result of a group scan."""

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


def scan_directory(
    path: Path,
    config: ScanConfig | None = None,
) -> ScanResult:
    """Scan a directory for files."""
    config = config or ScanConfig()
    result = ScanResult()
    start = time.monotonic()

    _walk(path, 0, config, result)
    result.scan_time = time.monotonic() - start
    return result


def _walk(
    directory: Path,
    depth: int,
    config: ScanConfig,
    result: ScanResult,
) -> None:
    """Walk directory tree."""
    if depth > config.max_depth:
        return

    try:
        entries = list(os.scandir(directory))
    except (PermissionError, OSError):
        result.errors.append(f"Cannot read: {directory}")
        return

    for entry in entries:
        try:
            name = entry.name
            if config.skip_hidden and name.startswith("."):
                result.skipped += 1
                continue
            if name in config.ignore_patterns:
                result.skipped += 1
                continue
            if entry.is_symlink() and not config.follow_symlinks:
                result.skipped += 1
                continue
            if entry.is_dir(follow_symlinks=config.follow_symlinks):
                _walk(Path(entry.path), depth + 1, config, result)
            elif entry.is_file(follow_symlinks=config.follow_symlinks):
                fi = FileInfo.from_path(Path(entry.path), config.follow_symlinks)
                if fi:
                    result.files.append(fi)
        except (PermissionError, OSError):
            result.skipped += 1


def format_scan_result(result: ScanResult) -> str:
    """Format scan result as text."""
    lines = [
        f"Scan: {result.file_count:,} files, {format_size(result.total_size)}",
        f"  Time: {result.scan_time:.2f}s",
    ]
    if result.errors:
        lines.append(f"  Errors: {len(result.errors)}")
    if result.skipped:
        lines.append(f"  Skipped: {result.skipped:,}")
    return "\n".join(lines)
