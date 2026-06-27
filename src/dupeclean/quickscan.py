"""Quick scan mode for DupeClean.

A fast, lightweight scan that skips full hashing and focuses on
size-based duplicate detection. Useful for large directories
where a full scan would take too long.
"""

from __future__ import annotations

import time
from pathlib import Path

from .config import Config
from .models import (
    DuplicateGroup,
    FileInfo,
    ScanStats,
    format_duration,
    format_size,
)
from .scanner import Scanner


def quick_scan(
    path: Path,
    config: Config | None = None,
    max_depth: int = 3,
) -> tuple[list[FileInfo], ScanStats, list[DuplicateGroup]]:
    """Perform a quick scan using size-based duplicate detection.

    Much faster than a full scan because it skips hashing entirely.
    Duplicates are detected purely by file size, which gives
    false positives but is instant.

    Args:
        path: Directory to scan.
        config: Scanner configuration.
        max_depth: Maximum directory depth to scan.

    Returns:
        Tuple of (files, stats, potential_duplicate_groups).
    """
    config = config or Config()
    time.monotonic()

    scanner = Scanner(config.scanner)
    files, _dirs, stats = scanner.scan(path)

    # Size-based duplicate detection (no hashing)
    size_groups: dict[int, list[FileInfo]] = {}
    for fi in files:
        if fi.size > 0:
            size_groups.setdefault(fi.size, []).append(fi)

    groups: list[DuplicateGroup] = []
    group_id = 0
    for size, group_files in size_groups.items():
        if len(group_files) >= 2:
            groups.append(
                DuplicateGroup(
                    group_id=group_id,
                    hash_value=f"size_{size}",
                    file_size=size,
                    files=group_files,
                )
            )
            group_id += 1

    groups.sort(key=lambda g: g.wasted_space, reverse=True)

    # Update stats
    stats.duplicate_groups = len(groups)
    stats.duplicate_files = sum(g.count for g in groups)
    stats.wasted_space = sum(g.wasted_space for g in groups)

    return files, stats, groups


def format_quick_scan_result(
    path: Path,
    files: list[FileInfo],
    stats: ScanStats,
    groups: list[DuplicateGroup],
) -> str:
    """Format quick scan results as text."""
    lines = [
        f"Quick scan: {path}",
        f"  Files: {stats.total_files:,}",
        f"  Dirs:  {stats.total_dirs:,}",
        f"  Size:  {format_size(stats.total_size)}",
        f"  Time:  {format_duration(stats.scan_duration)}",
        "",
        f"  Potential duplicates (by size): {stats.duplicate_groups:,} groups",
        f"  Duplicate files: {stats.duplicate_files:,}",
        f"  Potential waste: {format_size(stats.wasted_space)}",
    ]

    if groups:
        lines.append("\n  Top potential duplicates:")
        for g in groups[:10]:
            names = ", ".join(f.path.name for f in g.files[:3])
            if g.count > 3:
                names += f" (+{g.count - 3} more)"
            lines.append(f"    {g.count}x {g.size_display}: {names}")

    return "\n".join(lines)
