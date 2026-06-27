"""Tests for DupeClean queue manager v2 module."""

from __future__ import annotations

from dupeclean.queue_manager_v2 import (
    QueueManagerV2,
    QueueTask,
    format_queue_manager_v2,
)


class TestQueueManagerV2:
    def test_add(self):
        mgr = QueueManagerV2()
        mgr.add(QueueTask(task_id="1", path="/a", action="delete"))
        assert mgr.pending_count == 1

    def test_pop(self):
        mgr = QueueManagerV2()
        mgr.add(QueueTask(task_id="1", path="/a", action="delete"))
        task = mgr.pop()
        assert task is not None
        assert task.task_id == "1"
        assert mgr.pending_count == 0

    def test_pop_empty(self):
        mgr = QueueManagerV2()
        assert mgr.pop() is None

    def test_priority_order(self):
        mgr = QueueManagerV2()
        mgr.add(QueueTask(task_id="low", path="/a", action="delete", priority=1))
        mgr.add(QueueTask(task_id="high", path="/b", action="delete", priority=10))
        task = mgr.pop()
        assert task is not None
        assert task.task_id == "high"

    def test_complete(self):
        mgr = QueueManagerV2()
        task = QueueTask(task_id="1", path="/a", action="delete", size=100)
        mgr.add(task)
        popped = mgr.pop()
        mgr.complete(popped)
        assert mgr.completed_count == 1

    def test_total_size(self):
        mgr = QueueManagerV2()
        mgr.add(QueueTask(task_id="1", path="/a", action="delete", size=100))
        mgr.add(QueueTask(task_id="2", path="/b", action="delete", size=200))
        assert mgr.total_size == 300


class TestQueueTask:
    def test_size_display(self):
        task = QueueTask(task_id="1", path="/a", action="delete", size=1024)
        assert "B" in task.size_display


class TestFormatQueueManagerV2:
    def test_basic(self):
        mgr = QueueManagerV2()
        mgr.add(QueueTask(task_id="1", path="/a", action="delete", size=100))
        text = format_queue_manager_v2(mgr)
        assert "1 pending" in text
