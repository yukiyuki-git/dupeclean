"""File deduplication cleanup scheduler task module for DupeClean.

Define and manage scheduled cleanup tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TaskConfig:
    """Configuration for a scheduled task."""

    name: str
    path: Path
    action: str  # "scan", "cleanup", "report"
    schedule: str = "daily"  # "hourly", "daily", "weekly", "monthly"
    enabled: bool = True
    config: dict = field(default_factory=dict)

    @property
    def schedule_display(self) -> str:
        return self.schedule.capitalize()


@dataclass
class TaskScheduler:
    """Manage scheduled cleanup tasks."""

    tasks: list[TaskConfig] = field(default_factory=list)

    def add(self, task: TaskConfig) -> None:
        self.tasks.append(task)

    def remove(self, name: str) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.name != name]
        return len(self.tasks) < before

    def get_by_name(self, name: str) -> TaskConfig | None:
        for task in self.tasks:
            if task.name == name:
                return task
        return None

    def enable(self, name: str) -> None:
        task = self.get_by_name(name)
        if task:
            task.enabled = True

    def disable(self, name: str) -> None:
        task = self.get_by_name(name)
        if task:
            task.enabled = False

    @property
    def count(self) -> int:
        return len(self.tasks)

    @property
    def enabled_count(self) -> int:
        return sum(1 for t in self.tasks if t.enabled)


def format_task_scheduler(scheduler: TaskScheduler) -> str:
    """Format task scheduler as text."""
    if not scheduler.tasks:
        return "No scheduled tasks."

    lines = [
        f"Task Scheduler: {scheduler.count} tasks ({scheduler.enabled_count} enabled)",
        "",
    ]
    for task in scheduler.tasks:
        status = "ON" if task.enabled else "OFF"
        lines.append(f"  [{status}] {task.name}: {task.action} {task.schedule_display}")
        lines.append(f"    Path: {task.path}")
    return "\n".join(lines)
