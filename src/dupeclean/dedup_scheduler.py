"""File deduplication scheduler module for DupeClean.

Schedule automatic dedup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScheduledDedup:
    """A scheduled dedup operation."""

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
        elapsed_hours = (time.time() - self.last_run) / 3600
        return elapsed_hours >= self.interval_hours

    @property
    def interval_display(self) -> str:
        hours = self.interval_hours
        if hours < 1:
            return f"{hours * 60:.0f}m"
        if hours < 24:
            return f"{hours:.0f}h"
        days = hours / 24
        return f"{days:.0f}d"


@dataclass
class DedupScheduler:
    """Manage scheduled dedup operations."""

    tasks: list[ScheduledDedup] = field(default_factory=list)

    def add_task(self, task: ScheduledDedup) -> None:
        self.tasks.append(task)

    def remove_task(self, name: str) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.name != name]
        return len(self.tasks) < before

    def get_due_tasks(self) -> list[ScheduledDedup]:
        return [t for t in self.tasks if t.is_due]

    def mark_complete(self, name: str) -> None:
        for task in self.tasks:
            if task.name == name:
                task.last_run = time.time()
                break

    def enable(self, name: str) -> None:
        for task in self.tasks:
            if task.name == name:
                task.enabled = True
                break

    def disable(self, name: str) -> None:
        for task in self.tasks:
            if task.name == name:
                task.enabled = False
                break

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    @property
    def enabled_count(self) -> int:
        return sum(1 for t in self.tasks if t.enabled)


def format_schedule_tasks(scheduler: DedupScheduler) -> str:
    """Format scheduled tasks as text."""
    if not scheduler.tasks:
        return "No scheduled tasks."

    lines = [
        f"Scheduled Tasks: {scheduler.task_count} ({scheduler.enabled_count} enabled)",
        "",
    ]

    for task in scheduler.tasks:
        status = "ON" if task.enabled else "OFF"
        due = "DUE" if task.is_due else "waiting"
        lines.append(f"  [{status}] {task.name}: every {task.interval_display} ({due})")
        lines.append(f"    Path: {task.path}")

    return "\n".join(lines)
