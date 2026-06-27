"""File deduplication cleanup queue manager for DupeClean.

Manage cleanup queues with priority and scheduling.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class QueueTask:
    """A task in the cleanup queue."""

    task_id: str
    path: str
    action: str
    size: int = 0
    priority: int = 0
    status: str = "pending"
    created_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self) -> None:
        if self.created_at == 0:
            self.created_at = time.time()

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class QueueManagerV2:
    """Manage cleanup queues."""

    tasks: list[QueueTask] = field(default_factory=list)
    completed: list[QueueTask] = field(default_factory=list)

    def add(self, task: QueueTask) -> None:
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def pop(self) -> QueueTask | None:
        if self.tasks:
            return self.tasks.pop(0)
        return None

    def complete(self, task: QueueTask) -> None:
        task.status = "completed"
        task.completed_at = time.time()
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


def format_queue_manager_v2(manager: QueueManagerV2) -> str:
    """Format queue manager status."""
    return (
        f"Queue: {manager.pending_count} pending, "
        f"{manager.completed_count} completed, "
        f"{format_size(manager.total_size)} remaining"
    )
