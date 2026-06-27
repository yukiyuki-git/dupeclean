"""File deduplication cleanup scheduler for DupeClean.

Schedule automated cleanup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CleanupJob:
    """A scheduled cleanup job."""

    name: str
    path: Path
    interval_hours: float = 24.0
    last_run: float = 0.0
    enabled: bool = True
    config: dict = field(default_factory=dict)

    @property
    def is_due(self) -> bool:
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
class SchedulerV2:
    """Manage scheduled cleanup jobs."""

    jobs: list[CleanupJob] = field(default_factory=list)

    def add(self, job: CleanupJob) -> None:
        self.jobs.append(job)

    def remove(self, name: str) -> bool:
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j.name != name]
        return len(self.jobs) < before

    def get_due(self) -> list[CleanupJob]:
        return [j for j in self.jobs if j.is_due]

    def mark_done(self, name: str) -> None:
        for job in self.jobs:
            if job.name == name:
                job.last_run = time.time()
                break

    def enable(self, name: str) -> None:
        for job in self.jobs:
            if job.name == name:
                job.enabled = True
                break

    def disable(self, name: str) -> None:
        for job in self.jobs:
            if job.name == name:
                job.enabled = False
                break

    @property
    def count(self) -> int:
        return len(self.jobs)

    @property
    def enabled_count(self) -> int:
        return sum(1 for j in self.jobs if j.enabled)


def format_scheduler_v2(scheduler: SchedulerV2) -> str:
    """Format scheduler status as text."""
    if not scheduler.jobs:
        return "No scheduled jobs."

    lines = [
        f"Scheduled Jobs: {scheduler.count} ({scheduler.enabled_count} enabled)",
        "",
    ]
    for job in scheduler.jobs:
        status = "ON" if job.enabled else "OFF"
        due = "DUE" if job.is_due else "waiting"
        lines.append(f"  [{status}] {job.name}: every {job.interval_display} ({due})")
        lines.append(f"    Path: {job.path}")
    return "\n".join(lines)
