"""File deduplication cleanup queue for DupeClean.

Enhanced cleanup queue with batch operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class CleanupTask:
    """A cleanup task."""

    task_id: str
    path: str
    action: str
    size: int = 0
    priority: int = 0
    status: str = "pending"

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupQueueV2:
    """Enhanced cleanup queue."""

    tasks: list[CleanupTask] = field(default_factory=list)
    completed: list[CleanupTask] = field(default_factory=list)

    def add(self, task: CleanupTask) -> None:
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def pop(self) -> CleanupTask | None:
        if self.tasks:
            return self.tasks.pop(0)
        return None

    def complete(self, task: CleanupTask) -> None:
        task.status = "completed"
        self.completed.append(task)

    def fail(self, task: CleanupTask) -> None:
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


def format_cleanup_queue_v2(queue: CleanupQueueV2) -> str:
    """Format queue status as text."""
    return (
        f"Queue: {queue.pending_count} pending, "
        f"{queue.completed_count} completed, "
        f"{format_size(queue.total_size)} remaining"
    )
