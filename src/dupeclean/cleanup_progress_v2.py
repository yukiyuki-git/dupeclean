"""File deduplication cleanup progress tracker for DupeClean.

Track cleanup progress with detailed metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .models import format_size


@dataclass
class ProgressMetricsV2:
    """Cleanup progress metrics."""

    total_groups: int = 0
    groups_processed: int = 0
    total_files: int = 0
    files_processed: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    bytes_freed: int = 0
    errors: int = 0
    start_time: float = 0.0

    @property
    def group_percentage(self) -> float:
        if self.total_groups == 0:
            return 0.0
        return min(100.0, self.groups_processed / self.total_groups * 100)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def rate(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.groups_processed / self.elapsed

    @property
    def eta(self) -> float | None:
        if self.groups_processed <= 0 or self.rate <= 0:
            return None
        remaining = self.total_groups - self.groups_processed
        return remaining / self.rate

    @property
    def freed_display(self) -> str:
        return format_size(self.bytes_freed)

    def update_group(self) -> None:
        self.groups_processed += 1

    def update_file(self, deleted: bool = False, hardlinked: bool = False, freed: int = 0) -> None:
        self.files_processed += 1
        if deleted:
            self.files_deleted += 1
        if hardlinked:
            self.files_hardlinked += 1
        self.bytes_freed += freed

    def render(self) -> str:
        bar_width = 30
        filled = min(bar_width, int(self.group_percentage / 100 * bar_width))
        bar = "█" * filled + "░" * (bar_width - filled)
        parts = [
            f"[{bar}] {self.group_percentage:5.1f}%",
            f"({self.groups_processed}/{self.total_groups})",
        ]
        if self.eta is not None:
            if self.eta < 60:
                parts.append(f"ETA {self.eta:.0f}s")
            else:
                parts.append(f"ETA {self.eta / 60:.1f}m")
        return " ".join(parts)


def create_progress_v2(total_groups: int, total_files: int = 0) -> ProgressMetricsV2:
    """Create progress tracker."""
    return ProgressMetricsV2(
        total_groups=total_groups,
        total_files=total_files,
        start_time=time.monotonic(),
    )
