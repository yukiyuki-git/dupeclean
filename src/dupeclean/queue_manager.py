"""File deduplication cleanup queue manager for DupeClean.

Manage cleanup operation queues.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class QueueTask:
    """A task in the cleanup queue."""

    task_id: str
    action: str
    path: str
    size: int = 0
    priority: int = 0
    status: str = "pending"  # pending, running, completed, failed

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class QueueManager:
    """Manage cleanup operation queue."""

    tasks: list[QueueTask] = field(default_factory=list)
    completed: list[QueueTask] = field(default_factory=list)
    on_complete: Callable[[QueueTask], None] | None = None

    def add(self, task: QueueTask) -> None:
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def pop(self) -> QueueTask | None:
        if self.tasks:
            return self.tasks.pop(0)
        return None

    def complete(self, task: QueueTask) -> None:
        task.status = "completed"
        self.completed.append(task)
        if self.on_complete:
            self.on_complete(task)

    def fail(self, task: QueueTask) -> None:
        task.status = "failed"
        self.completed.append(task)

    @property
    def pending_count(self) -> int:
        return len(self.tasks)

    @property
    def completed_count(self) -> int:
        return len(self.completed)

    @property
    def total_size(self) -> int:
        return sum(t.size for t in self.tasks)

    @property
    def completed_size(self) -> int:
        return sum(t.size for t in self.completed if t.status == "completed")


def format_queue_manager(manager: QueueManager) -> str:
    """Format queue manager status."""
    return (
        f"Queue: {manager.pending_count} pending, "
        f"{manager.completed_count} completed, "
        f"{format_size(manager.total_size)} remaining"
    )
