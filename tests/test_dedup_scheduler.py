"""Tests for DupeClean dedup scheduler module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.dedup_scheduler import (
    DedupScheduler,
    ScheduledDedup,
    format_schedule_tasks,
)


class TestScheduledDedup:
    def test_is_due_default(self):
        task = ScheduledDedup(name="test", path=Path("/test"))
        assert task.is_due is True

    def test_is_due_after_run(self):
        task = ScheduledDedup(
            name="test",
            path=Path("/test"),
            interval_hours=24,
            last_run=time.time(),
        )
        assert task.is_due is False

    def test_is_due_after_interval(self):
        task = ScheduledDedup(
            name="test",
            path=Path("/test"),
            interval_hours=0.001,  # ~3.6 seconds
            last_run=time.time() - 10,
        )
        assert task.is_due is True

    def test_disabled_not_due(self):
        task = ScheduledDedup(
            name="test",
            path=Path("/test"),
            enabled=False,
        )
        assert task.is_due is False

    def test_interval_display_hours(self):
        task = ScheduledDedup(name="test", path=Path("/test"), interval_hours=12)
        assert "h" in task.interval_display

    def test_interval_display_days(self):
        task = ScheduledDedup(name="test", path=Path("/test"), interval_hours=48)
        assert "d" in task.interval_display


class TestDedupScheduler:
    def test_add_task(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="test", path=Path("/test")))
        assert scheduler.task_count == 1

    def test_remove_task(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="test", path=Path("/test")))
        assert scheduler.remove_task("test") is True
        assert scheduler.task_count == 0

    def test_remove_nonexistent(self):
        scheduler = DedupScheduler()
        assert scheduler.remove_task("nope") is False

    def test_get_due_tasks(self):
        scheduler = DedupScheduler()
        scheduler.add_task(
            ScheduledDedup(
                name="due",
                path=Path("/test"),
                interval_hours=0.001,
                last_run=0,
            )
        )
        scheduler.add_task(
            ScheduledDedup(
                name="not_due",
                path=Path("/test"),
                interval_hours=24,
                last_run=time.time(),
            )
        )
        due = scheduler.get_due_tasks()
        assert len(due) == 1
        assert due[0].name == "due"

    def test_mark_complete(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="test", path=Path("/test"), last_run=0))
        scheduler.mark_complete("test")
        assert scheduler.tasks[0].last_run > 0

    def test_enable_disable(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="test", path=Path("/test")))
        scheduler.disable("test")
        assert scheduler.tasks[0].enabled is False
        scheduler.enable("test")
        assert scheduler.tasks[0].enabled is True

    def test_enabled_count(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="a", path=Path("/a")))
        scheduler.add_task(ScheduledDedup(name="b", path=Path("/b"), enabled=False))
        assert scheduler.enabled_count == 1


class TestFormatScheduleTasks:
    def test_empty(self):
        scheduler = DedupScheduler()
        assert "No scheduled" in format_schedule_tasks(scheduler)

    def test_with_tasks(self):
        scheduler = DedupScheduler()
        scheduler.add_task(ScheduledDedup(name="daily", path=Path("/test")))
        text = format_schedule_tasks(scheduler)
        assert "daily" in text
