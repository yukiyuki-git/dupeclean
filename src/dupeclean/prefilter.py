"""File deduplication optimization module for DupeClean.

Optimize dedup operations for better performance.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import FileInfo


@dataclass
class OptimizationResult:
    """Result of a dedup optimization pass."""

    files_processed: int = 0
    files_skipped: int = 0
    time_saved_estimate: float = 0.0
    method: str = ""

    @property
    def efficiency(self) -> float:
        total = self.files_processed + self.files_skipped
        if total == 0:
            return 0.0
        return self.files_skipped / total


def optimize_by_size_prefilter(
    files: list[FileInfo],
) -> tuple[list[FileInfo], list[FileInfo]]:
    """Pre-filter files by size to skip unique sizes.

    Files with unique sizes can't be duplicates, so skip them.

    Returns:
        (candidates, skipped) tuple.
    """
    from collections import Counter

    size_counts = Counter(f.size for f in files)
    candidates = [f for f in files if size_counts[f.size] >= 2]
    skipped = [f for f in files if size_counts[f.size] < 2]
    return candidates, skipped


def optimize_by_inode(
    files: list[FileInfo],
) -> tuple[list[FileInfo], list[FileInfo]]:
    """Pre-filter files by inode to find hardlinks.

    Files with the same inode are already hardlinks.

    Returns:
        (unique, hardlinked) tuple.
    """
    seen_inodes: dict[tuple, FileInfo] = {}
    unique: list[FileInfo] = []
    hardlinked: list[FileInfo] = []

    for fi in files:
        if fi.inode is not None:
            key = (fi.path.parent, fi.inode)
            if key in seen_inodes:
                hardlinked.append(fi)
            else:
                seen_inodes[key] = fi
                unique.append(fi)
        else:
            unique.append(fi)

    return unique, hardlinked


def optimize_batch_size(total_files: int, available_memory_mb: int = 512) -> int:
    """Calculate optimal batch size for processing.

    Args:
        total_files: Total number of files.
        available_memory_mb: Available memory in MB.

    Returns:
        Recommended batch size.
    """
    # Rough estimate: ~1KB per file for metadata
    max_by_memory = available_memory_mb * 1024
    # Don't go below 100 or above total
    batch = min(total_files, max(100, max_by_memory))
    return batch


@dataclass
class PrefilterStats:
    """Statistics from pre-filtering."""

    original_count: int = 0
    candidate_count: int = 0
    skipped_count: int = 0
    hardlink_count: int = 0

    @property
    def reduction_pct(self) -> float:
        if self.original_count == 0:
            return 0.0
        return (self.original_count - self.candidate_count) / self.original_count * 100


def run_prefilter(
    files: list[FileInfo],
) -> tuple[list[FileInfo], PrefilterStats]:
    """Run all pre-filters to reduce dedup workload.

    Returns:
        (candidates, stats) tuple.
    """
    stats = PrefilterStats(original_count=len(files))

    # Size pre-filter
    candidates, skipped = optimize_by_size_prefilter(files)
    stats.skipped_count += len(skipped)

    # Inode pre-filter
    candidates, hardlinked = optimize_by_inode(candidates)
    stats.hardlink_count += len(hardlinked)
    stats.skipped_count += len(hardlinked)

    stats.candidate_count = len(candidates)
    return candidates, stats


def format_prefilter_stats(stats: PrefilterStats) -> str:
    """Format prefilter stats as text."""
    return (
        f"Prefilter: {stats.original_count:,} files -> "
        f"{stats.candidate_count:,} candidates "
        f"({stats.reduction_pct:.1f}% reduction)\n"
        f"  Skipped: {stats.skipped_count:,} "
        f"(unique sizes + hardlinks)\n"
        f"  Hardlinks found: {stats.hardlink_count:,}"
    )
