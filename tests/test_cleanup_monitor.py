"""Tests for DupeClean cleanup monitor module."""

from __future__ import annotations

from dupeclean.cleanup_monitor import (
    CleanupMonitorV2,
    MonitorUpdate,
    format_monitor_v2,
)


class TestCleanupMonitorV2:
    def test_start(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        assert monitor.is_running is True
        assert monitor.update_count == 1

    def test_update(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        monitor.update("progress", "Processing files")
        assert monitor.update_count == 2

    def test_complete(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        monitor.complete("Done")
        assert monitor.is_running is False
        assert monitor.update_count == 2

    def test_error(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        monitor.error("Something went wrong")
        assert monitor.update_count == 2

    def test_stop(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        monitor.stop()
        assert monitor.is_running is False

    def test_elapsed(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        assert monitor.elapsed >= 0

    def test_get_recent(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        for i in range(20):
            monitor.update("progress", f"Step {i}")
        recent = monitor.get_recent(5)
        assert len(recent) == 5


class TestFormatMonitorV2:
    def test_idle(self):
        monitor = CleanupMonitorV2()
        text = format_monitor_v2(monitor)
        assert "IDLE" in text

    def test_running(self):
        monitor = CleanupMonitorV2()
        monitor.start()
        text = format_monitor_v2(monitor)
        assert "RUNNING" in text


class TestMonitorUpdate:
    def test_defaults(self):
        update = MonitorUpdate(timestamp=0, event="test", message="msg")
        assert update.data == {}
