"""File deduplication cleanup summary for DupeClean.

Generate summaries of cleanup operations.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import format_size


@dataclass
class CleanupSummary:
    """Summary of a cleanup operation."""

    operation_id: str
    files_before: int = 0
    files_after: int = 0
    size_before: int = 0
    size_after: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    duration: float = 0.0
    errors: int = 0

    @property
    def space_freed(self) -> int:
        return self.size_before - self.size_after

    @property
    def space_freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def reduction_pct(self) -> float:
        if self.size_before == 0:
            return 0.0
        return (self.space_freed / self.size_before) * 100

    @property
    def files_removed(self) -> int:
        return self.files_before - self.files_after


def create_summary(
    operation_id: str,
    files_before: int,
    size_before: int,
    files_deleted: int = 0,
    files_hardlinked: int = 0,
    errors: int = 0,
    duration: float = 0.0,
) -> CleanupSummary:
    """Create a cleanup summary."""
    return CleanupSummary(
        operation_id=operation_id,
        files_before=files_before,
        files_after=files_before - files_deleted,
        size_before=size_before,
        size_after=size_before,  # Updated after actual cleanup
        files_deleted=files_deleted,
        files_hardlinked=files_hardlinked,
        duration=duration,
        errors=errors,
    )


def format_cleanup_summary(summary: CleanupSummary) -> str:
    """Format cleanup summary as text."""
    lines = [
        f"Cleanup Summary: {summary.operation_id}",
        "=" * 40,
        f"  Files before: {summary.files_before:,}",
        f"  Files after:  {summary.files_after:,}",
        f"  Files removed: {summary.files_removed:,}",
        f"  Deleted: {summary.files_deleted:,}",
        f"  Hardlinked: {summary.files_hardlinked:,}",
        f"  Errors: {summary.errors}",
        f"  Duration: {summary.duration:.1f}s",
        "",
        f"  Size before: {format_size(summary.size_before)}",
        f"  Size after:  {format_size(summary.size_after)}",
        f"  Freed:       {summary.space_freed_display} ({summary.reduction_pct:.1f}%)",
    ]
    return "\n".join(lines)


def format_brief_summary(summary: CleanupSummary) -> str:
    """Format a brief one-line summary."""
    return (
        f"{summary.files_deleted + summary.files_hardlinked} actions, "
        f"{summary.space_freed_display} freed "
        f"({summary.reduction_pct:.1f}%), "
        f"{summary.errors} errors"
    )
