"""Tests for DupeClean queue v2 module."""

from __future__ import annotations

from dupeclean.queue_v2 import (
    CleanupQueueV2,
    QueueItemV2,
    format_queue_v2,
)


class TestCleanupQueueV2:
    def test_add(self):
        queue = CleanupQueueV2()
        queue.add(QueueItemV2(item_id="1", path="/a", action="delete"))
        assert queue.pending_count == 1

    def test_pop(self):
        queue = CleanupQueueV2()
        queue.add(QueueItemV2(item_id="1", path="/a", action="delete"))
        item = queue.pop()
        assert item is not None
        assert item.item_id == "1"
        assert item.is_running

    def test_pop_empty(self):
        queue = CleanupQueueV2()
        assert queue.pop() is None

    def test_priority_order(self):
        queue = CleanupQueueV2()
        queue.add(QueueItemV2(item_id="low", path="/a", action="delete", priority=1))
        queue.add(QueueItemV2(item_id="high", path="/b", action="delete", priority=10))
        item = queue.pop()
        assert item is not None
        assert item.item_id == "high"

    def test_complete(self):
        queue = CleanupQueueV2()
        item = QueueItemV2(item_id="1", path="/a", action="delete", size=100)
        queue.add(item)
        popped = queue.pop()
        queue.complete(popped)
        assert queue.completed_count == 1

    def test_total_size(self):
        queue = CleanupQueueV2()
        queue.add(QueueItemV2(item_id="1", path="/a", action="delete", size=100))
        queue.add(QueueItemV2(item_id="2", path="/b", action="delete", size=200))
        assert queue.total_size == 300


class TestQueueItemV2:
    def test_size_display(self):
        item = QueueItemV2(item_id="1", path="/a", action="delete", size=1024)
        assert "B" in item.size_display

    def test_is_pending(self):
        item = QueueItemV2(item_id="1", path="/a", action="delete")
        assert item.is_pending is True


class TestFormatQueueV2:
    def test_basic(self):
        queue = CleanupQueueV2()
        queue.add(QueueItemV2(item_id="1", path="/a", action="delete", size=100))
        text = format_queue_v2(queue)
        assert "1 pending" in text
