"""Tests for DupeClean cleanup queue v2 module."""

from __future__ import annotations

from dupeclean.cleanup_queue_v2 import (
    CleanupQueueV2,
    CleanupTask,
    format_cleanup_queue_v2,
)


class TestCleanupQueueV2:
    def test_add(self):
        queue = CleanupQueueV2()
        queue.add(CleanupTask(task_id="1", path="/a", action="delete"))
        assert queue.pending_count == 1

    def test_pop(self):
        queue = CleanupQueueV2()
        queue.add(CleanupTask(task_id="1", path="/a", action="delete"))
        task = queue.pop()
        assert task is not None
        assert task.task_id == "1"

    def test_pop_empty(self):
        queue = CleanupQueueV2()
        assert queue.pop() is None

    def test_priority_order(self):
        queue = CleanupQueueV2()
        queue.add(CleanupTask(task_id="low", path="/a", action="delete", priority=1))
        queue.add(CleanupTask(task_id="high", path="/b", action="delete", priority=10))
        task = queue.pop()
        assert task is not None
        assert task.task_id == "high"

    def test_complete(self):
        queue = CleanupQueueV2()
        task = CleanupTask(task_id="1", path="/a", action="delete", size=100)
        queue.add(task)
        popped = queue.pop()
        queue.complete(popped)
        assert queue.completed_count == 1

    def test_fail(self):
        queue = CleanupQueueV2()
        task = CleanupTask(task_id="1", path="/a", action="delete")
        queue.add(task)
        popped = queue.pop()
        queue.fail(popped)
        assert queue.completed_count == 1

    def test_total_size(self):
        queue = CleanupQueueV2()
        queue.add(CleanupTask(task_id="1", path="/a", action="delete", size=100))
        queue.add(CleanupTask(task_id="2", path="/b", action="delete", size=200))
        assert queue.total_size == 300


class TestCleanupTask:
    def test_size_display(self):
        task = CleanupTask(task_id="1", path="/a", action="delete", size=1024)
        assert "B" in task.size_display


class TestFormatCleanupQueueV2:
    def test_basic(self):
        queue = CleanupQueueV2()
        queue.add(CleanupTask(task_id="1", path="/a", action="delete", size=100))
        text = format_cleanup_queue_v2(queue)
        assert "1 pending" in text
