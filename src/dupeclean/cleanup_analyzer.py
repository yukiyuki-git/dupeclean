"""File deduplication cleanup analyzer for DupeClean.

Analyze cleanup operations for effectiveness.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import format_size


@dataclass
class CleanupAnalysis:
    """Analysis of cleanup effectiveness."""

    total_groups: int = 0
    groups_cleaned: int = 0
    total_files: int = 0
    files_removed: int = 0
    space_before: int = 0
    space_freed: int = 0

    @property
    def cleanup_rate(self) -> float:
        if self.total_groups == 0:
            return 0.0
        return self.groups_cleaned / self.total_groups

    @property
    def file_reduction(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.files_removed / self.total_files

    @property
    def space_reduction(self) -> float:
        if self.space_before == 0:
            return 0.0
        return (self.space_freed / self.space_before) * 100

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


def analyze_cleanup(
    total_groups: int,
    groups_cleaned: int,
    total_files: int,
    files_removed: int,
    space_before: int,
    space_freed: int,
) -> CleanupAnalysis:
    """Analyze cleanup effectiveness."""
    return CleanupAnalysis(
        total_groups=total_groups,
        groups_cleaned=groups_cleaned,
        total_files=total_files,
        files_removed=files_removed,
        space_before=space_before,
        space_freed=space_freed,
    )


def format_cleanup_analysis(analysis: CleanupAnalysis) -> str:
    """Format cleanup analysis as text."""
    return (
        f"Cleanup Analysis:\n"
        f"  Groups: {analysis.groups_cleaned}/{analysis.total_groups} "
        f"({analysis.cleanup_rate:.1%})\n"
        f"  Files removed: {analysis.files_removed:,}/{analysis.total_files:,} "
        f"({analysis.file_reduction:.1%})\n"
        f"  Space freed: {analysis.freed_display} "
        f"({analysis.space_reduction:.1f}%)"
    )
