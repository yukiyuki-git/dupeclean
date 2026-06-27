"""File deduplication file stats module for DupeClean.

Comprehensive file statistics and analysis.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import FileInfo, format_size


@dataclass
class FileStatsV2:
    """Comprehensive file statistics."""

    total_files: int = 0
    total_size: int = 0
    min_size: int = 0
    max_size: int = 0
    avg_size: float = 0.0
    median_size: float = 0.0
    stdev_size: float = 0.0
    p25_size: float = 0.0
    p75_size: float = 0.0
    p95_size: float = 0.0
    p99_size: float = 0.0

    @property
    def total_display(self) -> str:
        return format_size(self.total_size)

    @property
    def avg_display(self) -> str:
        return format_size(int(self.avg_size))

    @property
    def median_display(self) -> str:
        return format_size(int(self.median_size))


def compute_file_stats(files: list[FileInfo]) -> FileStatsV2:
    """Compute comprehensive file statistics."""
    if not files:
        return FileStatsV2()

    sizes = sorted(f.size for f in files)
    n = len(sizes)

    return FileStatsV2(
        total_files=n,
        total_size=sum(sizes),
        min_size=sizes[0],
        max_size=sizes[-1],
        avg_size=statistics.mean(sizes),
        median_size=statistics.median(sizes),
        stdev_size=statistics.stdev(sizes) if n > 1 else 0,
        p25_size=sizes[max(0, int(n * 0.25))],
        p75_size=sizes[max(0, int(n * 0.75))],
        p95_size=sizes[max(0, int(n * 0.95))],
        p99_size=sizes[max(0, int(n * 0.99))],
    )


def format_file_stats_v2(stats: FileStatsV2) -> str:
    """Format file stats as text."""
    if stats.total_files == 0:
        return "No files to analyze."

    return (
        f"File Statistics ({stats.total_files:,} files):\n"
        f"  Total:   {stats.total_display}\n"
        f"  Min:     {format_size(stats.min_size)}\n"
        f"  Max:     {format_size(stats.max_size)}\n"
        f"  Mean:    {stats.avg_display}\n"
        f"  Median:  {stats.median_display}\n"
        f"  Std Dev: {format_size(int(stats.stdev_size))}\n"
        f"  P25:     {format_size(stats.p25_size)}\n"
        f"  P75:     {format_size(stats.p75_size)}\n"
        f"  P95:     {format_size(stats.p95_size)}\n"
        f"  P99:     {format_size(stats.p99_size)}"
    )
