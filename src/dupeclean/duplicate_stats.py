"""File deduplication duplicate statistics module for DupeClean.

Statistical analysis of duplicate files.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import DuplicateGroup, format_size


@dataclass
class DuplicateStats:
    """Statistical analysis of duplicates."""
    total_groups: int = 0
    total_files: int = 0
    total_wasted: int = 0
    avg_group_size: float = 0.0
    median_group_size: float = 0.0
    max_group_size: int = 0
    avg_file_size: float = 0.0
    largest_waste_group: int = -1

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)

    @property
    def dedup_ratio(self) -> float:
        if self.total_files == 0 or self.avg_file_size <= 0:
            return 0.0
        return self.total_wasted / (self.total_files * self.avg_file_size)


def compute_duplicate_stats(groups: list[DuplicateGroup]) -> DuplicateStats:
    """Compute statistics for duplicate groups."""
    if not groups:
        return DuplicateStats()

    group_sizes = [g.count for g in groups]
    file_sizes = [g.file_size for g in groups]
    wasted = [g.wasted_space for g in groups]

    largest = max(groups, key=lambda g: g.wasted_space)

    return DuplicateStats(
        total_groups=len(groups),
        total_files=sum(group_sizes),
        total_wasted=sum(wasted),
        avg_group_size=statistics.mean(group_sizes),
        median_group_size=statistics.median(group_sizes),
        max_group_size=max(group_sizes),
        avg_file_size=statistics.mean(file_sizes),
        largest_waste_group=largest.group_id,
    )


def format_duplicate_stats(stats: DuplicateStats) -> str:
    """Format duplicate stats as text."""
    if stats.total_groups == 0:
        return "No duplicates found."

    return (
        f"Duplicate Statistics:\n"
        f"  Groups: {stats.total_groups:,}\n"
        f"  Total files: {stats.total_files:,}\n"
        f"  Wasted: {stats.wasted_display}\n"
        f"  Avg group size: {stats.avg_group_size:.1f}\n"
        f"  Median group size: {stats.median_group_size:.0f}\n"
        f"  Max group size: {stats.max_group_size}\n"
        f"  Avg file size: {format_size(int(stats.avg_file_size))}"
    )
