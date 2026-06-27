"""File deduplication cleanup tracker for DupeClean.

Track cleanup operations with detailed statistics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class TrackerEntry:
    """A tracked cleanup operation."""

    timestamp: float
    operation: str
    files_count: int = 0
    space_freed: int = 0
    duration: float = 0.0
    success: bool = True

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


@dataclass
class CleanupTracker:
    """Track cleanup operations over time."""

    entries: list[TrackerEntry] = field(default_factory=list)

    def track(
        self,
        operation: str,
        files_count: int = 0,
        space_freed: int = 0,
        duration: float = 0.0,
        success: bool = True,
    ) -> None:
        """Track a cleanup operation."""
        self.entries.append(
            TrackerEntry(
                timestamp=time.time(),
                operation=operation,
                files_count=files_count,
                space_freed=space_freed,
                duration=duration,
                success=success,
            )
        )

    @property
    def total_operations(self) -> int:
        return len(self.entries)

    @property
    def total_freed(self) -> int:
        return sum(e.space_freed for e in self.entries)

    @property
    def total_files(self) -> int:
        return sum(e.files_count for e in self.entries)

    def get_recent(self, count: int = 10) -> list[TrackerEntry]:
        return self.entries[-count:]

    def get_by_operation(self, operation: str) -> list[TrackerEntry]:
        return [e for e in self.entries if e.operation == operation]


def format_tracker(tracker: CleanupTracker) -> str:
    """Format tracker as text."""
    if not tracker.total_operations:
        return "No tracked operations."

    lines = [
        f"Tracker: {tracker.total_operations} operations",
        f"  Total freed: {format_size(tracker.total_freed)}",
        f"  Total files: {tracker.total_files:,}",
    ]

    recent = tracker.get_recent(5)
    if recent:
        lines.append("\n  Recent:")
        for entry in reversed(recent):
            import datetime

            dt = datetime.datetime.fromtimestamp(entry.timestamp)
            status = "[+]" if entry.success else "[X]"
            lines.append(
                f"    {status} [{dt.strftime('%H:%M')}] "
                f"{entry.operation}: {entry.files_count} files, "
                f"{entry.freed_display} freed"
            )

    return "\n".join(lines)
