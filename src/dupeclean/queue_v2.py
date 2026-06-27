"""File deduplication cleanup queue v2 for DupeClean.

Enhanced cleanup queue with priority and batching.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class QueueItemV2:
    """An enhanced queue item."""

    item_id: str
    path: str
    action: str
    size: int = 0
    priority: int = 0
    status: str = "pending"
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self) -> None:
        if self.created_at == 0:
            self.created_at = time.time()

    @property
    def size_display(self) -> str:
        return format_size(self.size)

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_running(self) -> bool:
        return self.status == "running"

    @property
    def is_complete(self) -> bool:
        return self.status in ("completed", "failed")


@dataclass
class CleanupQueueV2:
    """Enhanced cleanup queue."""

    items: list[QueueItemV2] = field(default_factory=list)
    completed: list[QueueItemV2] = field(default_factory=list)

    def add(self, item: QueueItemV2) -> None:
        self.items.append(item)
        self.items.sort(key=lambda i: i.priority, reverse=True)

    def pop(self) -> QueueItemV2 | None:
        if self.items:
            item = self.items.pop(0)
            item.status = "running"
            item.started_at = time.time()
            return item
        return None

    def complete(self, item: QueueItemV2, success: bool = True) -> None:
        item.status = "completed" if success else "failed"
        item.completed_at = time.time()
        self.completed.append(item)

    @property
    def pending_count(self) -> int:
        return len(self.items)

    @property
    def completed_count(self) -> int:
        return len(self.completed)

    @property
    def total_size(self) -> int:
        return sum(i.size for i in self.items)

    @property
    def completed_size(self) -> int:
        return sum(i.size for i in self.completed if i.status == "completed")


def format_queue_v2(queue: CleanupQueueV2) -> str:
    """Format queue status as text."""
    return (
        f"Queue: {queue.pending_count} pending, "
        f"{queue.completed_count} completed, "
        f"{format_size(queue.total_size)} remaining"
    )
