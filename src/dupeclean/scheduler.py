"""Cleanup scheduler for DupeClean.

Schedule automatic cleanup tasks that run periodically.
Supports cron-like scheduling and one-time tasks.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScheduledTask:
    """A scheduled cleanup task."""

    name: str
    path: Path
    action: str  # "scan", "clean_dupes", "report"
    interval_seconds: float = 86400  # Default: daily
    last_run: float = 0.0
    enabled: bool = True
    args: dict = field(default_factory=dict)

    @property
    def is_due(self) -> bool:
        """Check if this task is due to run."""
        if not self.enabled:
            return False
        return time.time() - self.last_run >= self.interval_seconds

    @property
    def interval_display(self) -> str:
        seconds = self.interval_seconds
        if seconds < 60:
            return f"{seconds:.0f}s"
        if seconds < 3600:
            return f"{seconds / 60:.0f}m"
        if seconds < 86400:
            return f"{seconds / 3600:.0f}h"
        return f"{seconds / 86400:.0f}d"


@dataclass
class SchedulerConfig:
    """Scheduler configuration."""

    tasks: list[ScheduledTask] = field(default_factory=list)
    max_history: int = 100
    history: list[dict] = field(default_factory=list)

    def add_task(self, task: ScheduledTask) -> None:
        """Add a task to the scheduler."""
        self.tasks.append(task)

    def remove_task(self, name: str) -> bool:
        """Remove a task by name."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.name != name]
        return len(self.tasks) < before

    def get_due_tasks(self) -> list[ScheduledTask]:
        """Get all tasks that are due to run."""
        return [t for t in self.tasks if t.is_due]

    def record_run(self, task_name: str, success: bool, message: str = "") -> None:
        """Record a task run in history."""
        self.history.append(
            {
                "task": task_name,
                "time": time.time(),
                "success": success,
                "message": message,
            }
        )
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    def save(self, path: Path) -> None:
        """Save scheduler config to file."""
        data = {
            "tasks": [
                {
                    "name": t.name,
                    "path": str(t.path),
                    "action": t.action,
                    "interval": t.interval_seconds,
                    "enabled": t.enabled,
                    "args": t.args,
                }
                for t in self.tasks
            ],
            "history": self.history[-50:],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> SchedulerConfig:
        """Load scheduler config from file."""
        if not path.exists():
            return cls()

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()

        config = cls()
        for t in data.get("tasks", []):
            config.tasks.append(
                ScheduledTask(
                    name=t["name"],
                    path=Path(t["path"]),
                    action=t["action"],
                    interval_seconds=t.get("interval", 86400),
                    enabled=t.get("enabled", True),
                    args=t.get("args", {}),
                )
            )
        config.history = data.get("history", [])
        return config


def format_schedule(config: SchedulerConfig) -> str:
    """Format scheduler config as text."""
    if not config.tasks:
        return "No scheduled tasks."

    lines = ["Scheduled Tasks:", ""]
    for task in config.tasks:
        status = "ON" if task.enabled else "OFF"
        due = "DUE" if task.is_due else "waiting"
        lines.append(
            f"  [{status}] {task.name}: {task.action} every {task.interval_display} ({due})"
        )
        lines.append(f"    Path: {task.path}")

    if config.history:
        lines.append(f"\n  Recent history ({len(config.history)} runs):")
        for entry in config.history[-5:]:
            status = "OK" if entry["success"] else "FAIL"
            lines.append(f"    [{status}] {entry['task']}: {entry.get('message', '')}")

    return "\n".join(lines)
