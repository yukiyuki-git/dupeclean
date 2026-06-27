"""File deduplication cleanup scheduler integration for DupeClean.

Integrate cleanup with the scheduler for automated operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScheduledCleanup:
    """A scheduled cleanup task."""

    name: str
    path: Path
    action: str  # "scan", "cleanup", "report"
    interval_hours: float = 24.0
    last_run: float = 0.0
    enabled: bool = True

    @property
    def is_due(self) -> bool:
        import time

        if not self.enabled:
            return False
        return (time.time() - self.last_run) / 3600 >= self.interval_hours

    @property
    def interval_display(self) -> str:
        hours = self.interval_hours
        if hours < 1:
            return f"{hours * 60:.0f}m"
        if hours < 24:
            return f"{hours:.0f}h"
        return f"{hours / 24:.0f}d"


@dataclass
class CleanupScheduler:
    """Manage scheduled cleanup tasks."""

    tasks: list[ScheduledCleanup] = field(default_factory=list)

    def add(self, task: ScheduledCleanup) -> None:
        self.tasks.append(task)

    def remove(self, name: str) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.name != name]
        return len(self.tasks) < before

    def get_due(self) -> list[ScheduledCleanup]:
        return [t for t in self.tasks if t.is_due]

    def mark_done(self, name: str) -> None:
        import time

        for task in self.tasks:
            if task.name == name:
                task.last_run = time.time()
                break

    @property
    def count(self) -> int:
        return len(self.tasks)

    @property
    def enabled_count(self) -> int:
        return sum(1 for t in self.tasks if t.enabled)


def format_scheduled_cleanups(scheduler: CleanupScheduler) -> str:
    """Format scheduled cleanups as text."""
    if not scheduler.tasks:
        return "No scheduled cleanups."

    lines = [
        f"Scheduled Cleanups: {scheduler.count} ({scheduler.enabled_count} enabled)",
        "",
    ]
    for task in scheduler.tasks:
        status = "ON" if task.enabled else "OFF"
        due = "DUE" if task.is_due else "waiting"
        lines.append(
            f"  [{status}] {task.name}: {task.action} every {task.interval_display} ({due})"
        )
        lines.append(f"    Path: {task.path}")
    return "\n".join(lines)
