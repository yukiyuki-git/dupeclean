"""File statistics module for DupeClean.

Comprehensive statistical analysis of file collections.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import FileInfo, format_size


@dataclass
class FileStats:
    """Statistical summary of a file collection."""

    count: int
    total_size: int
    min_size: int
    max_size: int
    mean_size: float
    median_size: float
    stdev_size: float
    p25_size: float
    p75_size: float
    p95_size: float

    @property
    def total_display(self) -> str:
        return format_size(self.total_size)

    @property
    def mean_display(self) -> str:
        return format_size(int(self.mean_size))

    @property
    def median_display(self) -> str:
        return format_size(int(self.median_size))


def compute_stats(files: list[FileInfo]) -> FileStats:
    """Compute statistics for a file collection."""
    if not files:
        return FileStats(
            count=0,
            total_size=0,
            min_size=0,
            max_size=0,
            mean_size=0,
            median_size=0,
            stdev_size=0,
            p25_size=0,
            p75_size=0,
            p95_size=0,
        )

    sizes = [f.size for f in files]
    sizes.sort()

    n = len(sizes)
    p25_idx = max(0, int(n * 0.25))
    p75_idx = max(0, int(n * 0.75))
    p95_idx = max(0, int(n * 0.95))

    return FileStats(
        count=n,
        total_size=sum(sizes),
        min_size=sizes[0],
        max_size=sizes[-1],
        mean_size=statistics.mean(sizes),
        median_size=statistics.median(sizes),
        stdev_size=statistics.stdev(sizes) if n > 1 else 0,
        p25_size=sizes[p25_idx],
        p75_size=sizes[p75_idx],
        p95_size=sizes[p95_idx],
    )


def format_file_stats(stats: FileStats) -> str:
    """Format file statistics as text."""
    if stats.count == 0:
        return "No files to analyze."

    lines = [
        f"File Statistics ({stats.count:,} files):",
        f"  Total:   {stats.total_display}",
        f"  Min:     {format_size(stats.min_size)}",
        f"  Max:     {format_size(stats.max_size)}",
        f"  Mean:    {stats.mean_display}",
        f"  Median:  {stats.median_display}",
        f"  Std Dev: {format_size(int(stats.stdev_size))}",
        f"  P25:     {format_size(stats.p25_size)}",
        f"  P75:     {format_size(stats.p75_size)}",
        f"  P95:     {format_size(stats.p95_size)}",
    ]
    return "\n".join(lines)


def compute_extension_stats(
    files: list[FileInfo],
) -> dict[str, FileStats]:
    """Compute statistics per extension."""
    by_ext: dict[str, list[FileInfo]] = {}
    for fi in files:
        ext = fi.ext or "(none)"
        by_ext.setdefault(ext, []).append(fi)

    return {ext: compute_stats(ext_files) for ext, ext_files in by_ext.items()}


def format_extension_stats(
    ext_stats: dict[str, FileStats],
) -> str:
    """Format per-extension statistics as text."""
    sorted_stats = sorted(
        ext_stats.items(),
        key=lambda x: x[1].total_size,
        reverse=True,
    )

    lines = [
        f"Extension Statistics ({len(ext_stats)} types):",
        "",
        f"  {'Ext':<12s} {'Count':>8s} {'Total':>10s} {'Mean':>10s} {'Median':>10s}",
        "  " + "-" * 55,
    ]

    for ext, stats in sorted_stats[:20]:
        lines.append(
            f"  .{ext:<11s} {stats.count:>8,} "
            f"{format_size(stats.total_size):>10s} "
            f"{format_size(int(stats.mean_size)):>10s} "
            f"{format_size(int(stats.median_size)):>10s}"
        )

    return "\n".join(lines)
