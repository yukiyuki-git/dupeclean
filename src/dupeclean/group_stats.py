"""File deduplication duplicate group stats module for DupeClean.

Statistical analysis of duplicate groups.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import DuplicateGroup, format_size


@dataclass
class GroupStats:
    """Statistics for duplicate groups."""

    total_groups: int = 0
    total_files: int = 0
    total_wasted: int = 0
    avg_files_per_group: float = 0.0
    median_files_per_group: float = 0.0
    max_files_in_group: int = 0
    avg_group_size: float = 0.0
    median_group_size: float = 0.0

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)

    @property
    def dedup_potential(self) -> float:
        if self.total_files == 0 or self.avg_group_size <= 0:
            return 0.0
        return self.total_wasted / (self.total_files * self.avg_group_size)


def compute_group_stats(groups: list[DuplicateGroup]) -> GroupStats:
    """Compute statistics for duplicate groups."""
    if not groups:
        return GroupStats()

    files_per_group = [g.count for g in groups]
    sizes = [g.file_size for g in groups]
    wasted = [g.wasted_space for g in groups]

    return GroupStats(
        total_groups=len(groups),
        total_files=sum(files_per_group),
        total_wasted=sum(wasted),
        avg_files_per_group=statistics.mean(files_per_group),
        median_files_per_group=statistics.median(files_per_group),
        max_files_in_group=max(files_per_group),
        avg_group_size=statistics.mean(sizes),
        median_group_size=statistics.median(sizes),
    )


def format_group_stats(stats: GroupStats) -> str:
    """Format group stats as text."""
    if stats.total_groups == 0:
        return "No duplicate groups."

    return (
        f"Group Statistics:\n"
        f"  Groups: {stats.total_groups:,}\n"
        f"  Total files: {stats.total_files:,}\n"
        f"  Wasted: {stats.wasted_display}\n"
        f"  Avg files/group: {stats.avg_files_per_group:.1f}\n"
        f"  Median files/group: {stats.median_files_per_group:.0f}\n"
        f"  Max files/group: {stats.max_files_in_group}\n"
        f"  Avg group size: {format_size(int(stats.avg_group_size))}\n"
        f"  Median group size: {format_size(int(stats.median_group_size))}"
    )
