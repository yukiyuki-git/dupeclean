"""File deduplication progress tracking for DupeClean.

Track progress of long-running dedup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class ProgressTracker:
    """Track progress of dedup operations."""

    total: int = 0
    current: int = 0
    stage: str = ""
    start_time: float = 0.0
    _last_update: float = 0.0

    def start(self, total: int, stage: str = "") -> None:
        """Start tracking progress."""
        self.total = total
        self.current = 0
        self.stage = stage
        self.start_time = time.monotonic()
        self._last_update = self.start_time

    def update(self, increment: int = 1, stage: str = "") -> None:
        """Update progress."""
        self.current += increment
        if stage:
            self.stage = stage
        self._last_update = time.monotonic()

    def set(self, value: int, stage: str = "") -> None:
        """Set absolute progress."""
        self.current = value
        if stage:
            self.stage = stage

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def eta(self) -> float | None:
        """Estimated time remaining in seconds."""
        if self.current <= 0 or self.total <= 0:
            return None
        if self.current >= self.total:
            return 0.0
        rate = self.current / self.elapsed if self.elapsed > 0 else 0
        if rate <= 0:
            return None
        return (self.total - self.current) / rate

    @property
    def rate(self) -> float:
        """Items per second."""
        if self.elapsed <= 0:
            return 0.0
        return self.current / self.elapsed

    @property
    def is_complete(self) -> bool:
        return self.current >= self.total


def format_progress(tracker: ProgressTracker) -> str:
    """Format progress as text."""
    bar_width = 30
    filled = min(bar_width, int(tracker.percentage / 100 * bar_width))
    bar = "█" * filled + "░" * (bar_width - filled)

    parts = [
        f"[{bar}] {tracker.percentage:5.1f}%",
        f"({tracker.current:,}/{tracker.total:,})",
    ]

    if tracker.stage:
        parts.append(tracker.stage)

    if tracker.eta is not None:
        if tracker.eta < 60:
            parts.append(f"ETA: {tracker.eta:.0f}s")
        else:
            parts.append(f"ETA: {tracker.eta / 60:.1f}m")

    if tracker.rate > 0:
        parts.append(f"({tracker.rate:,.0f}/s)")

    return " ".join(parts)
