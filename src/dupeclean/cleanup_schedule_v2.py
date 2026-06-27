"""File deduplication group cleanup scheduler for DupeClean.

Schedule automated cleanup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CleanupSchedule:
    """A scheduled cleanup task."""

    name: str
    path: Path
    interval_hours: float = 24.0
    strategy: str = "shortest"
    action: str = "hardlink"
    enabled: bool = True
    last_run: float = 0.0

    @property
    def is_due(self) -> bool:
        if not self.enabled:
            return False
        return (time.time() - self.last_run) / 3600 >= self.interval_hours

    @property
    def interval_display(self) -> str:
        h = self.interval_hours
        if h < 1:
            return f"{h * 60:.0f}m"
        if h < 24:
            return f"{h:.0f}h"
        return f"{h / 24:.0f}d"


@dataclass
class CleanupSchedulerV2:
    """Manage cleanup schedules."""

    schedules: list[CleanupSchedule] = field(default_factory=list)

    def add(self, schedule: CleanupSchedule) -> None:
        self.schedules.append(schedule)

    def remove(self, name: str) -> bool:
        before = len(self.schedules)
        self.schedules = [s for s in self.schedules if s.name != name]
        return len(self.schedules) < before

    def get_due(self) -> list[CleanupSchedule]:
        return [s for s in self.schedules if s.is_due]

    def mark_done(self, name: str) -> None:
        for s in self.schedules:
            if s.name == name:
                s.last_run = time.time()
                break

    @property
    def count(self) -> int:
        return len(self.schedules)

    @property
    def enabled_count(self) -> int:
        return sum(1 for s in self.schedules if s.enabled)


def format_cleanup_schedule(scheduler: CleanupSchedulerV2) -> str:
    """Format schedule as text."""
    if not scheduler.schedules:
        return "No scheduled cleanups."

    lines = [
        f"Schedules: {scheduler.count} ({scheduler.enabled_count} enabled)",
        "",
    ]
    for s in scheduler.schedules:
        status = "ON" if s.enabled else "OFF"
        due = "DUE" if s.is_due else "waiting"
        lines.append(f"  [{status}] {s.name}: {s.action} every {s.interval_display} ({due})")
        lines.append(f"    Path: {s.path}")
    return "\n".join(lines)
