"""Tests for DupeClean scheduler v3 module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.scheduler_v3 import (
    CronSchedule,
    ScheduledTaskV2,
    SchedulerV3,
    format_cron_schedule,
)


class TestCronSchedule:
    def test_matches_any(self):
        schedule = CronSchedule()
        assert schedule.matches(time.time()) is True

    def test_matches_specific_minute(self):
        import datetime

        now = datetime.datetime(2024, 1, 1, 12, 30)
        ts = now.timestamp()
        schedule = CronSchedule(minute="30")
        assert schedule.matches(ts) is True

    def test_no_match_minute(self):
        import datetime

        now = datetime.datetime(2024, 1, 1, 12, 30)
        ts = now.timestamp()
        schedule = CronSchedule(minute="45")
        assert schedule.matches(ts) is False


class TestScheduledTaskV2:
    def test_is_due_default(self):
        schedule = CronSchedule()
        task = ScheduledTaskV2(name="test", path=Path("/test"), schedule=schedule)
        assert task.is_due() is True

    def test_disabled_not_due(self):
        schedule = CronSchedule()
        task = ScheduledTaskV2(name="test", path=Path("/test"), schedule=schedule, enabled=False)
        assert task.is_due() is False


class TestSchedulerV3:
    def test_add(self):
        scheduler = SchedulerV3()
        scheduler.add(ScheduledTaskV2(name="test", path=Path("/test"), schedule=CronSchedule()))
        assert scheduler.count == 1

    def test_remove(self):
        scheduler = SchedulerV3()
        scheduler.add(ScheduledTaskV2(name="test", path=Path("/test"), schedule=CronSchedule()))
        assert scheduler.remove("test") is True
        assert scheduler.count == 0

    def test_get_due(self):
        scheduler = SchedulerV3()
        scheduler.add(ScheduledTaskV2(name="always", path=Path("/test"), schedule=CronSchedule()))
        due = scheduler.get_due()
        assert len(due) == 1


class TestFormatCronSchedule:
    def test_wildcard(self):
        schedule = CronSchedule()
        text = format_cron_schedule(schedule)
        assert "*" in text

    def test_specific(self):
        schedule = CronSchedule(minute="30", hour="12")
        text = format_cron_schedule(schedule)
        assert "30" in text
        assert "12" in text
