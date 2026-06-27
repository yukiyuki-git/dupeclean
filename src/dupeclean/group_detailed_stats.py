"""File deduplication group statistics for DupeClean.

Detailed statistics for duplicate groups.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import DuplicateGroup, format_size


@dataclass
class DetailedGroupStats:
    """Detailed statistics for groups."""

    total_groups: int = 0
    total_files: int = 0
    total_unique_size: int = 0
    total_wasted: int = 0
    avg_files_per_group: float = 0.0
    median_files_per_group: float = 0.0
    max_files_in_group: int = 0
    avg_file_size: float = 0.0
    median_file_size: float = 0.0
    largest_group_id: int = -1
    most_wasted_group_id: int = -1

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)

    @property
    def unique_display(self) -> str:
        return format_size(self.total_unique_size)

    @property
    def dedup_ratio(self) -> float:
        total = self.total_unique_size + self.total_wasted
        if total == 0:
            return 0.0
        return self.total_wasted / total


def compute_detailed_stats(groups: list[DuplicateGroup]) -> DetailedGroupStats:
    """Compute detailed statistics for groups."""
    if not groups:
        return DetailedGroupStats()

    files_per_group = [g.count for g in groups]
    file_sizes = [g.file_size for g in groups]
    wasted = [g.wasted_space for g in groups]

    largest = max(groups, key=lambda g: g.count)
    most_wasted = max(groups, key=lambda g: g.wasted_space)

    return DetailedGroupStats(
        total_groups=len(groups),
        total_files=sum(files_per_group),
        total_unique_size=sum(g.file_size for g in groups),
        total_wasted=sum(wasted),
        avg_files_per_group=statistics.mean(files_per_group),
        median_files_per_group=statistics.median(files_per_group),
        max_files_in_group=max(files_per_group),
        avg_file_size=statistics.mean(file_sizes),
        median_file_size=statistics.median(file_sizes),
        largest_group_id=largest.group_id,
        most_wasted_group_id=most_wasted.group_id,
    )


def format_detailed_stats(stats: DetailedGroupStats) -> str:
    """Format detailed stats as text."""
    if stats.total_groups == 0:
        return "No duplicate groups."

    return (
        f"Detailed Group Statistics:\n"
        f"  Groups: {stats.total_groups:,}\n"
        f"  Total files: {stats.total_files:,}\n"
        f"  Unique size: {stats.unique_display}\n"
        f"  Wasted: {stats.wasted_display}\n"
        f"  Dedup ratio: {stats.dedup_ratio:.1%}\n"
        f"\n"
        f"  Group sizes:\n"
        f"    Average: {stats.avg_files_per_group:.1f}\n"
        f"    Median: {stats.median_files_per_group:.0f}\n"
        f"    Max: {stats.max_files_in_group}\n"
        f"\n"
        f"  File sizes:\n"
        f"    Average: {format_size(int(stats.avg_file_size))}\n"
        f"    Median: {format_size(int(stats.median_file_size))}\n"
        f"\n"
        f"  Largest group: #{stats.largest_group_id}\n"
        f"  Most wasted: #{stats.most_wasted_group_id}"
    )
