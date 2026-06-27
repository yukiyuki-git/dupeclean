"""Tests for DupeClean cleanup scheduler."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.scheduler import (
    ScheduledTask,
    SchedulerConfig,
    format_schedule,
)


class TestScheduledTask:
    def test_is_due_default(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
        )
        assert task.is_due is True

    def test_is_due_after_run(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
            interval_seconds=3600,
            last_run=time.time(),
        )
        assert task.is_due is False

    def test_is_due_after_interval(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
            interval_seconds=1,
            last_run=time.time() - 2,
        )
        assert task.is_due is True

    def test_disabled_not_due(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
            enabled=False,
        )
        assert task.is_due is False

    def test_interval_display_seconds(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
            interval_seconds=30,
        )
        assert "s" in task.interval_display

    def test_interval_display_hours(self):
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
            interval_seconds=7200,
        )
        assert "h" in task.interval_display


class TestSchedulerConfig:
    def test_add_task(self):
        config = SchedulerConfig()
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
        )
        config.add_task(task)
        assert len(config.tasks) == 1

    def test_remove_task(self):
        config = SchedulerConfig()
        task = ScheduledTask(
            name="test",
            path=Path("/test"),
            action="scan",
        )
        config.add_task(task)
        assert config.remove_task("test") is True
        assert len(config.tasks) == 0

    def test_remove_nonexistent(self):
        config = SchedulerConfig()
        assert config.remove_task("nope") is False

    def test_get_due_tasks(self):
        config = SchedulerConfig()
        config.add_task(
            ScheduledTask(
                name="due",
                path=Path("/test"),
                action="scan",
                interval_seconds=1,
                last_run=0,
            )
        )
        config.add_task(
            ScheduledTask(
                name="not_due",
                path=Path("/test"),
                action="scan",
                interval_seconds=3600,
                last_run=time.time(),
            )
        )
        due = config.get_due_tasks()
        assert len(due) == 1
        assert due[0].name == "due"

    def test_record_run(self):
        config = SchedulerConfig()
        config.record_run("test", True, "success")
        assert len(config.history) == 1
        assert config.history[0]["success"] is True

    def test_max_history(self):
        config = SchedulerConfig(max_history=5)
        for i in range(10):
            config.record_run(f"task_{i}", True)
        assert len(config.history) == 5

    def test_save_and_load(self, tmp_path):
        config = SchedulerConfig()
        config.add_task(
            ScheduledTask(
                name="test",
                path=Path("/test"),
                action="scan",
                interval_seconds=3600,
            )
        )
        config.record_run("test", True, "ok")

        save_path = tmp_path / "scheduler.json"
        config.save(save_path)
        assert save_path.exists()

        loaded = SchedulerConfig.load(save_path)
        assert len(loaded.tasks) == 1
        assert loaded.tasks[0].name == "test"
        assert len(loaded.history) == 1

    def test_load_nonexistent(self, tmp_path):
        config = SchedulerConfig.load(tmp_path / "nope")
        assert len(config.tasks) == 0


class TestFormatSchedule:
    def test_empty(self):
        config = SchedulerConfig()
        assert "No scheduled" in format_schedule(config)

    def test_with_tasks(self):
        config = SchedulerConfig()
        config.add_task(
            ScheduledTask(
                name="daily",
                path=Path("/test"),
                action="scan",
                interval_seconds=86400,
            )
        )
        text = format_schedule(config)
        assert "daily" in text
        assert "scan" in text
