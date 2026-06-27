"""File deduplication statistics module for DupeClean.

Statistical analysis of dedup operations.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import DuplicateGroup, format_size


@dataclass
class DedupStats:
    """Statistical analysis of duplicate groups."""

    total_groups: int = 0
    total_duplicates: int = 0
    total_unique_size: int = 0
    total_wasted: int = 0
    avg_group_size: float = 0.0
    median_group_size: float = 0.0
    max_group_size: int = 0
    avg_file_size: float = 0.0
    largest_group: DuplicateGroup | None = None

    @property
    def dedup_ratio(self) -> float:
        if self.total_duplicates == 0:
            return 0.0
        return self.total_wasted / (self.total_unique_size + self.total_wasted)


def compute_dedup_stats(
    groups: list[DuplicateGroup],
) -> DedupStats:
    """Compute statistics for duplicate groups."""
    if not groups:
        return DedupStats()

    group_sizes = [g.count for g in groups]
    file_sizes = [g.file_size for g in groups]
    wasted = [g.wasted_space for g in groups]

    largest = max(groups, key=lambda g: g.wasted_space)

    return DedupStats(
        total_groups=len(groups),
        total_duplicates=sum(group_sizes),
        total_unique_size=sum(g.file_size for g in groups),
        total_wasted=sum(wasted),
        avg_group_size=statistics.mean(group_sizes),
        median_group_size=statistics.median(group_sizes),
        max_group_size=max(group_sizes),
        avg_file_size=statistics.mean(file_sizes),
        largest_group=largest,
    )


def format_dedup_stats(stats: DedupStats) -> str:
    """Format dedup stats as text."""
    if stats.total_groups == 0:
        return "No duplicates found."

    lines = [
        "Dedup Statistics:",
        f"  Groups: {stats.total_groups:,}",
        f"  Total duplicates: {stats.total_duplicates:,}",
        f"  Unique size: {format_size(stats.total_unique_size)}",
        f"  Wasted: {format_size(stats.total_wasted)}",
        f"  Dedup ratio: {stats.dedup_ratio:.1%}",
        "",
        "  Group sizes:",
        f"    Average: {stats.avg_group_size:.1f}",
        f"    Median: {stats.median_group_size:.0f}",
        f"    Max: {stats.max_group_size}",
        "",
        f"  Avg file size: {format_size(int(stats.avg_file_size))}",
    ]

    if stats.largest_group:
        g = stats.largest_group
        lines.extend(
            [
                "",
                "  Largest waste group:",
                f"    Group #{g.group_id}: {g.count} files, {g.wasted_display} wasted",
            ]
        )

    return "\n".join(lines)


def compute_size_distribution(
    groups: list[DuplicateGroup],
) -> dict[str, int]:
    """Compute size distribution of duplicate groups."""
    buckets = {
        "tiny (<1KB)": 0,
        "small (1-64KB)": 0,
        "medium (64KB-1MB)": 0,
        "large (1-16MB)": 0,
        "huge (>16MB)": 0,
    }

    for g in groups:
        if g.file_size < 1024:
            buckets["tiny (<1KB)"] += 1
        elif g.file_size < 65536:
            buckets["small (1-64KB)"] += 1
        elif g.file_size < 1048576:
            buckets["medium (64KB-1MB)"] += 1
        elif g.file_size < 16777216:
            buckets["large (1-16MB)"] += 1
        else:
            buckets["huge (>16MB)"] += 1

    return buckets
