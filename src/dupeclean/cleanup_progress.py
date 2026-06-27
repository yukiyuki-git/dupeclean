"""File deduplication cleanup progress module for DupeClean.

Track cleanup progress with detailed metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .models import format_size


@dataclass
class ProgressMetrics:
    """Cleanup progress metrics."""

    files_total: int = 0
    files_processed: int = 0
    files_succeeded: int = 0
    files_failed: int = 0
    bytes_total: int = 0
    bytes_processed: int = 0
    start_time: float = 0.0

    @property
    def percentage(self) -> float:
        if self.files_total == 0:
            return 0.0
        return min(100.0, self.files_processed / self.files_total * 100)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def rate(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.files_processed / self.elapsed

    @property
    def eta(self) -> float | None:
        if self.files_processed <= 0 or self.rate <= 0:
            return None
        remaining = self.files_total - self.files_processed
        return remaining / self.rate

    @property
    def success_rate(self) -> float:
        if self.files_processed == 0:
            return 0.0
        return self.files_succeeded / self.files_processed

    @property
    def bytes_display(self) -> str:
        return format_size(self.bytes_processed)

    def update(self, count: int = 1, bytes_count: int = 0, success: bool = True) -> None:
        """Update progress."""
        self.files_processed += count
        self.bytes_processed += bytes_count
        if success:
            self.files_succeeded += count
        else:
            self.files_failed += count

    def render(self) -> str:
        """Render progress as text."""
        bar_width = 30
        filled = min(bar_width, int(self.percentage / 100 * bar_width))
        bar = "█" * filled + "░" * (bar_width - filled)

        parts = [
            f"[{bar}] {self.percentage:5.1f}%",
            f"({self.files_processed}/{self.files_total})",
        ]

        if self.eta is not None:
            if self.eta < 60:
                parts.append(f"ETA {self.eta:.0f}s")
            else:
                parts.append(f"ETA {self.eta / 60:.1f}m")

        return " ".join(parts)


def create_progress(total_files: int, total_bytes: int = 0) -> ProgressMetrics:
    """Create progress metrics."""
    return ProgressMetrics(
        files_total=total_files,
        bytes_total=total_bytes,
        start_time=time.monotonic(),
    )
