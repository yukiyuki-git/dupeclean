"""Tests for DupeClean cleanup queue module."""

from __future__ import annotations

from dupeclean.cleanup_queue import (
    CleanupQueue,
    QueueItem,
    format_queue,
)


class TestCleanupQueue:
    def test_add(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/a", action="delete", size=100))
        assert queue.pending_count == 1

    def test_pop(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/a", action="delete", size=100))
        item = queue.pop()
        assert item is not None
        assert item.path == "/a"
        assert queue.pending_count == 0

    def test_pop_empty(self):
        queue = CleanupQueue()
        assert queue.pop() is None

    def test_priority_order(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/low", action="delete", priority=1))
        queue.add(QueueItem(path="/high", action="delete", priority=10))
        item = queue.pop()
        assert item is not None
        assert item.path == "/high"

    def test_mark_done(self):
        queue = CleanupQueue()
        item = QueueItem(path="/a", action="delete", size=100)
        queue.add(item)
        popped = queue.pop()
        queue.mark_done(popped)
        assert queue.processed_count == 1

    def test_mark_error(self):
        queue = CleanupQueue()
        item = QueueItem(path="/a", action="delete")
        queue.add(item)
        popped = queue.pop()
        queue.mark_error(popped, "Permission denied")
        assert len(queue.errors) == 1

    def test_total_size(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/a", action="delete", size=100))
        queue.add(QueueItem(path="/b", action="delete", size=200))
        assert queue.total_size == 300

    def test_is_empty(self):
        queue = CleanupQueue()
        assert queue.is_empty is True
        queue.add(QueueItem(path="/a", action="delete"))
        assert queue.is_empty is False

    def test_progress(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/a", action="delete"))
        queue.add(QueueItem(path="/b", action="delete"))
        item = queue.pop()
        queue.mark_done(item)
        assert queue.progress == 0.5


class TestQueueItem:
    def test_size_display(self):
        item = QueueItem(path="/a", action="delete", size=1024)
        assert "B" in item.size_display


class TestFormatQueue:
    def test_basic(self):
        queue = CleanupQueue()
        queue.add(QueueItem(path="/a", action="delete", size=100))
        text = format_queue(queue)
        assert "1 pending" in text
