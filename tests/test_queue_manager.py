"""Tests for DupeClean queue manager module."""

from __future__ import annotations

from dupeclean.queue_manager import (
    QueueManager,
    QueueTask,
    format_queue_manager,
)


class TestQueueManager:
    def test_add(self):
        mgr = QueueManager()
        mgr.add(QueueTask(task_id="1", action="delete", path="/a"))
        assert mgr.pending_count == 1

    def test_pop(self):
        mgr = QueueManager()
        mgr.add(QueueTask(task_id="1", action="delete", path="/a"))
        task = mgr.pop()
        assert task is not None
        assert task.task_id == "1"
        assert mgr.pending_count == 0

    def test_pop_empty(self):
        mgr = QueueManager()
        assert mgr.pop() is None

    def test_priority_order(self):
        mgr = QueueManager()
        mgr.add(QueueTask(task_id="low", action="delete", path="/a", priority=1))
        mgr.add(QueueTask(task_id="high", action="delete", path="/b", priority=10))
        task = mgr.pop()
        assert task is not None
        assert task.task_id == "high"

    def test_complete(self):
        mgr = QueueManager()
        task = QueueTask(task_id="1", action="delete", path="/a", size=100)
        mgr.add(task)
        popped = mgr.pop()
        mgr.complete(popped)
        assert mgr.completed_count == 1

    def test_fail(self):
        mgr = QueueManager()
        task = QueueTask(task_id="1", action="delete", path="/a")
        mgr.add(task)
        popped = mgr.pop()
        mgr.fail(popped)
        assert mgr.completed_count == 1

    def test_on_complete_callback(self):
        completed = []
        mgr = QueueManager(on_complete=lambda t: completed.append(t))
        task = QueueTask(task_id="1", action="delete", path="/a")
        mgr.add(task)
        popped = mgr.pop()
        mgr.complete(popped)
        assert len(completed) == 1

    def test_total_size(self):
        mgr = QueueManager()
        mgr.add(QueueTask(task_id="1", action="delete", path="/a", size=100))
        mgr.add(QueueTask(task_id="2", action="delete", path="/b", size=200))
        assert mgr.total_size == 300


class TestQueueTask:
    def test_size_display(self):
        task = QueueTask(task_id="1", action="delete", path="/a", size=1024)
        assert "B" in task.size_display


class TestFormatQueueManager:
    def test_basic(self):
        mgr = QueueManager()
        mgr.add(QueueTask(task_id="1", action="delete", path="/a", size=100))
        text = format_queue_manager(mgr)
        assert "1 pending" in text
