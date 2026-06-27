"""File deduplication cleanup scheduler v2 for DupeClean.

Enhanced scheduler with cron-like scheduling.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CronSchedule:
    """A cron-like schedule."""

    minute: str = "*"
    hour: str = "*"
    day: str = "*"
    month: str = "*"
    weekday: str = "*"

    def matches(self, timestamp: float) -> bool:
        """Check if timestamp matches this schedule."""
        import datetime

        dt = datetime.datetime.fromtimestamp(timestamp)
        return (
            self._matches_field(dt.minute, self.minute)
            and self._matches_field(dt.hour, self.hour)
            and self._matches_field(dt.day, self.day)
            and self._matches_field(dt.month, self.month)
            and self._matches_field(dt.weekday(), self.weekday)
        )

    def _matches_field(self, value: int, pattern: str) -> bool:
        if pattern == "*":
            return True
        return value == int(pattern)


@dataclass
class ScheduledTaskV2:
    """A scheduled task with cron support."""

    name: str
    path: Path
    schedule: CronSchedule
    action: str = "scan"
    enabled: bool = True
    last_run: float = 0.0

    def is_due(self, timestamp: float | None = None) -> bool:
        if not self.enabled:
            return False
        ts = timestamp or time.time()
        return self.schedule.matches(ts)


@dataclass
class SchedulerV3:
    """Enhanced scheduler with cron support."""

    tasks: list[ScheduledTaskV2] = field(default_factory=list)

    def add(self, task: ScheduledTaskV2) -> None:
        self.tasks.append(task)

    def remove(self, name: str) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.name != name]
        return len(self.tasks) < before

    def get_due(self, timestamp: float | None = None) -> list[ScheduledTaskV2]:
        return [t for t in self.tasks if t.is_due(timestamp)]

    def mark_done(self, name: str) -> None:
        for task in self.tasks:
            if task.name == name:
                task.last_run = time.time()
                break

    @property
    def count(self) -> int:
        return len(self.tasks)


def format_cron_schedule(schedule: CronSchedule) -> str:
    """Format cron schedule as text."""
    return f"{schedule.minute} {schedule.hour} {schedule.day} {schedule.month} {schedule.weekday}"
