"""Tests for DupeClean scheduler v2 module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.scheduler_v2 import (
    CleanupJob,
    SchedulerV2,
    format_scheduler_v2,
)


class TestCleanupJob:
    def test_is_due_default(self):
        job = CleanupJob(name="test", path=Path("/test"))
        assert job.is_due is True

    def test_is_due_after_run(self):
        job = CleanupJob(name="test", path=Path("/test"), interval_hours=24, last_run=time.time())
        assert job.is_due is False

    def test_is_due_after_interval(self):
        job = CleanupJob(
            name="test", path=Path("/test"), interval_hours=0.001, last_run=time.time() - 10
        )
        assert job.is_due is True

    def test_disabled_not_due(self):
        job = CleanupJob(name="test", path=Path("/test"), enabled=False)
        assert job.is_due is False

    def test_interval_display_hours(self):
        job = CleanupJob(name="t", path=Path("/t"), interval_hours=12)
        assert "h" in job.interval_display

    def test_interval_display_days(self):
        job = CleanupJob(name="t", path=Path("/t"), interval_hours=48)
        assert "d" in job.interval_display


class TestSchedulerV2:
    def test_add(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="test", path=Path("/t")))
        assert scheduler.count == 1

    def test_remove(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="test", path=Path("/t")))
        assert scheduler.remove("test") is True
        assert scheduler.count == 0

    def test_get_due(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="due", path=Path("/t"), interval_hours=0.001, last_run=0))
        scheduler.add(
            CleanupJob(name="not_due", path=Path("/t"), interval_hours=24, last_run=time.time())
        )
        due = scheduler.get_due()
        assert len(due) == 1

    def test_mark_done(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="test", path=Path("/t"), last_run=0))
        scheduler.mark_done("test")
        assert scheduler.jobs[0].last_run > 0

    def test_enable_disable(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="test", path=Path("/t")))
        scheduler.disable("test")
        assert scheduler.jobs[0].enabled is False
        scheduler.enable("test")
        assert scheduler.jobs[0].enabled is True

    def test_enabled_count(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="a", path=Path("/a")))
        scheduler.add(CleanupJob(name="b", path=Path("/b"), enabled=False))
        assert scheduler.enabled_count == 1


class TestFormatSchedulerV2:
    def test_empty(self):
        scheduler = SchedulerV2()
        assert "No scheduled" in format_scheduler_v2(scheduler)

    def test_with_jobs(self):
        scheduler = SchedulerV2()
        scheduler.add(CleanupJob(name="daily", path=Path("/t")))
        text = format_scheduler_v2(scheduler)
        assert "daily" in text
