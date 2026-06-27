"""Tests for DupeClean task scheduler module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.task_scheduler import (
    TaskConfig,
    TaskScheduler,
    format_task_scheduler,
)


class TestTaskScheduler:
    def test_add(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="test", path=Path("/test"), action="scan"))
        assert scheduler.count == 1

    def test_remove(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="test", path=Path("/test"), action="scan"))
        assert scheduler.remove("test") is True
        assert scheduler.count == 0

    def test_remove_nonexistent(self):
        scheduler = TaskScheduler()
        assert scheduler.remove("nope") is False

    def test_get_by_name(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="test", path=Path("/test"), action="scan"))
        task = scheduler.get_by_name("test")
        assert task is not None
        assert task.name == "test"

    def test_get_by_name_nonexistent(self):
        scheduler = TaskScheduler()
        assert scheduler.get_by_name("nope") is None

    def test_enable_disable(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="test", path=Path("/test"), action="scan"))
        scheduler.disable("test")
        assert scheduler.tasks[0].enabled is False
        scheduler.enable("test")
        assert scheduler.tasks[0].enabled is True

    def test_enabled_count(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="a", path=Path("/a"), action="scan"))
        scheduler.add(TaskConfig(name="b", path=Path("/b"), action="scan", enabled=False))
        assert scheduler.enabled_count == 1


class TestTaskConfig:
    def test_schedule_display(self):
        config = TaskConfig(name="t", path=Path("/t"), action="scan", schedule="daily")
        assert config.schedule_display == "Daily"


class TestFormatTaskScheduler:
    def test_empty(self):
        scheduler = TaskScheduler()
        assert "No scheduled" in format_task_scheduler(scheduler)

    def test_with_tasks(self):
        scheduler = TaskScheduler()
        scheduler.add(TaskConfig(name="daily", path=Path("/t"), action="scan"))
        text = format_task_scheduler(scheduler)
        assert "daily" in text
