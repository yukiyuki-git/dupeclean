"""File deduplication cleanup statistics module for DupeClean.

Detailed statistics for cleanup operations.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import format_size


@dataclass
class CleanupStatsV2:
    """Detailed cleanup statistics."""

    files_scanned: int = 0
    files_analyzed: int = 0
    duplicates_found: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    files_skipped: int = 0
    errors: int = 0
    space_before: int = 0
    space_after: int = 0
    scan_duration: float = 0.0
    hash_duration: float = 0.0
    cleanup_duration: float = 0.0

    @property
    def space_freed(self) -> int:
        return self.space_before - self.space_after

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def reduction_pct(self) -> float:
        if self.space_before == 0:
            return 0.0
        return (self.space_freed / self.space_before) * 100

    @property
    def total_duration(self) -> float:
        return self.scan_duration + self.hash_duration + self.cleanup_duration

    @property
    def dedup_rate(self) -> float:
        if self.files_analyzed == 0:
            return 0.0
        return self.duplicates_found / self.files_analyzed


def format_stats_v2(stats: CleanupStatsV2) -> str:
    """Format cleanup stats as text."""
    return (
        f"Cleanup Statistics:\n"
        f"  Scanned: {stats.files_scanned:,}\n"
        f"  Analyzed: {stats.files_analyzed:,}\n"
        f"  Duplicates: {stats.duplicates_found:,}\n"
        f"  Deleted: {stats.files_deleted:,}\n"
        f"  Hardlinked: {stats.files_hardlinked:,}\n"
        f"  Errors: {stats.errors}\n"
        f"  Space before: {format_size(stats.space_before)}\n"
        f"  Space after: {format_size(stats.space_after)}\n"
        f"  Freed: {stats.freed_display} ({stats.reduction_pct:.1f}%)\n"
        f"  Duration: {stats.total_duration:.1f}s"
    )
