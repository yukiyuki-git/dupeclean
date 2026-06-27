"""Tests for DupeClean cleanup scheduler integration."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.cleanup_schedule import (
    CleanupScheduler,
    ScheduledCleanup,
    format_scheduled_cleanups,
)


class TestScheduledCleanup:
    def test_is_due_default(self):
        task = ScheduledCleanup(name="test", path=Path("/test"), action="scan")
        assert task.is_due is True

    def test_is_due_after_run(self):
        task = ScheduledCleanup(
            name="test", path=Path("/test"), action="scan", interval_hours=24, last_run=time.time()
        )
        assert task.is_due is False

    def test_is_due_after_interval(self):
        task = ScheduledCleanup(
            name="test",
            path=Path("/test"),
            action="scan",
            interval_hours=0.001,
            last_run=time.time() - 10,
        )
        assert task.is_due is True

    def test_disabled_not_due(self):
        task = ScheduledCleanup(name="test", path=Path("/test"), action="scan", enabled=False)
        assert task.is_due is False

    def test_interval_display_hours(self):
        task = ScheduledCleanup(name="t", path=Path("/t"), action="scan", interval_hours=12)
        assert "h" in task.interval_display

    def test_interval_display_days(self):
        task = ScheduledCleanup(name="t", path=Path("/t"), action="scan", interval_hours=48)
        assert "d" in task.interval_display


class TestCleanupScheduler:
    def test_add(self):
        scheduler = CleanupScheduler()
        scheduler.add(ScheduledCleanup(name="test", path=Path("/t"), action="scan"))
        assert scheduler.count == 1

    def test_remove(self):
        scheduler = CleanupScheduler()
        scheduler.add(ScheduledCleanup(name="test", path=Path("/t"), action="scan"))
        assert scheduler.remove("test") is True
        assert scheduler.count == 0

    def test_remove_nonexistent(self):
        scheduler = CleanupScheduler()
        assert scheduler.remove("nope") is False

    def test_get_due(self):
        scheduler = CleanupScheduler()
        scheduler.add(
            ScheduledCleanup(
                name="due", path=Path("/t"), action="scan", interval_hours=0.001, last_run=0
            )
        )
        scheduler.add(
            ScheduledCleanup(
                name="not_due",
                path=Path("/t"),
                action="scan",
                interval_hours=24,
                last_run=time.time(),
            )
        )
        due = scheduler.get_due()
        assert len(due) == 1
        assert due[0].name == "due"

    def test_mark_done(self):
        scheduler = CleanupScheduler()
        scheduler.add(ScheduledCleanup(name="test", path=Path("/t"), action="scan", last_run=0))
        scheduler.mark_done("test")
        assert scheduler.tasks[0].last_run > 0

    def test_enabled_count(self):
        scheduler = CleanupScheduler()
        scheduler.add(ScheduledCleanup(name="a", path=Path("/a"), action="scan"))
        scheduler.add(ScheduledCleanup(name="b", path=Path("/b"), action="scan", enabled=False))
        assert scheduler.enabled_count == 1


class TestFormatScheduledCleanups:
    def test_empty(self):
        scheduler = CleanupScheduler()
        assert "No scheduled" in format_scheduled_cleanups(scheduler)

    def test_with_tasks(self):
        scheduler = CleanupScheduler()
        scheduler.add(ScheduledCleanup(name="daily", path=Path("/t"), action="scan"))
        text = format_scheduled_cleanups(scheduler)
        assert "daily" in text
