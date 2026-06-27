"""Tests for DupeClean cleanup schedule v2 module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.cleanup_schedule_v2 import (
    CleanupSchedule,
    CleanupSchedulerV2,
    format_cleanup_schedule,
)


class TestCleanupSchedule:
    def test_is_due_default(self):
        s = CleanupSchedule(name="test", path=Path("/t"))
        assert s.is_due is True

    def test_is_due_after_run(self):
        s = CleanupSchedule(
            name="test",
            path=Path("/t"),
            interval_hours=24,
            last_run=time.time(),
        )
        assert s.is_due is False

    def test_is_due_after_interval(self):
        s = CleanupSchedule(
            name="test",
            path=Path("/t"),
            interval_hours=0.001,
            last_run=time.time() - 10,
        )
        assert s.is_due is True

    def test_disabled_not_due(self):
        s = CleanupSchedule(name="test", path=Path("/t"), enabled=False)
        assert s.is_due is False

    def test_interval_display_hours(self):
        s = CleanupSchedule(name="t", path=Path("/t"), interval_hours=12)
        assert "h" in s.interval_display

    def test_interval_display_days(self):
        s = CleanupSchedule(name="t", path=Path("/t"), interval_hours=48)
        assert "d" in s.interval_display


class TestCleanupSchedulerV2:
    def test_add(self):
        sch = CleanupSchedulerV2()
        sch.add(CleanupSchedule(name="test", path=Path("/t")))
        assert sch.count == 1

    def test_remove(self):
        sch = CleanupSchedulerV2()
        sch.add(CleanupSchedule(name="test", path=Path("/t")))
        assert sch.remove("test") is True
        assert sch.count == 0

    def test_get_due(self):
        sch = CleanupSchedulerV2()
        sch.add(
            CleanupSchedule(
                name="due",
                path=Path("/t"),
                interval_hours=0.001,
                last_run=0,
            )
        )
        sch.add(
            CleanupSchedule(
                name="not_due",
                path=Path("/t"),
                interval_hours=24,
                last_run=time.time(),
            )
        )
        due = sch.get_due()
        assert len(due) == 1

    def test_mark_done(self):
        sch = CleanupSchedulerV2()
        sch.add(CleanupSchedule(name="test", path=Path("/t"), last_run=0))
        sch.mark_done("test")
        assert sch.schedules[0].last_run > 0

    def test_enabled_count(self):
        sch = CleanupSchedulerV2()
        sch.add(CleanupSchedule(name="a", path=Path("/a")))
        sch.add(CleanupSchedule(name="b", path=Path("/b"), enabled=False))
        assert sch.enabled_count == 1


class TestFormatCleanupSchedule:
    def test_empty(self):
        sch = CleanupSchedulerV2()
        assert "No scheduled" in format_cleanup_schedule(sch)

    def test_with_schedules(self):
        sch = CleanupSchedulerV2()
        sch.add(CleanupSchedule(name="daily", path=Path("/t")))
        text = format_cleanup_schedule(sch)
        assert "daily" in text
