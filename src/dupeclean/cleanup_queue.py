"""File deduplication cleanup queue for DupeClean.

Queue cleanup operations for batch execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class QueueItem:
    """An item in the cleanup queue."""

    path: str
    action: str  # "delete", "hardlink", "move"
    size: int = 0
    priority: int = 0  # Higher = process first
    metadata: dict = field(default_factory=dict)

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupQueue:
    """Queue for cleanup operations."""

    items: list[QueueItem] = field(default_factory=list)
    processed: list[QueueItem] = field(default_factory=list)
    errors: list[tuple[QueueItem, str]] = field(default_factory=list)

    def add(self, item: QueueItem) -> None:
        self.items.append(item)
        self.items.sort(key=lambda i: i.priority, reverse=True)

    @property
    def pending_count(self) -> int:
        return len(self.items)

    @property
    def processed_count(self) -> int:
        return len(self.processed)

    @property
    def total_size(self) -> int:
        return sum(i.size for i in self.items)

    @property
    def processed_size(self) -> int:
        return sum(i.size for i in self.processed)

    def pop(self) -> QueueItem | None:
        """Get the next item from the queue."""
        if self.items:
            return self.items.pop(0)
        return None

    def mark_done(self, item: QueueItem) -> None:
        """Mark an item as processed."""
        self.processed.append(item)

    def mark_error(self, item: QueueItem, error: str) -> None:
        """Mark an item as failed."""
        self.errors.append((item, error))

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def progress(self) -> float:
        total = self.pending_count + self.processed_count
        if total == 0:
            return 0.0
        return self.processed_count / total


def format_queue(queue: CleanupQueue) -> str:
    """Format queue status as text."""
    lines = [
        f"Cleanup Queue: {queue.pending_count} pending, {queue.processed_count} processed",
        f"  Total size: {format_size(queue.total_size)}",
        f"  Processed: {format_size(queue.processed_size)}",
    ]
    if queue.errors:
        lines.append(f"  Errors: {len(queue.errors)}")
    return "\n".join(lines)
