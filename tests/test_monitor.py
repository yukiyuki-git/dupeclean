"""Tests for DupeClean cleanup monitor module."""

from __future__ import annotations

from dupeclean.monitor import (
    CleanupMonitor,
    MonitorEvent,
    format_monitor,
)


class TestCleanupMonitor:
    def test_start(self):
        monitor = CleanupMonitor()
        monitor.start()
        assert monitor.is_running is True
        assert monitor.event_count == 1

    def test_progress(self):
        monitor = CleanupMonitor()
        monitor.start()
        monitor.progress("Processing files")
        assert monitor.event_count == 2

    def test_complete(self):
        monitor = CleanupMonitor()
        monitor.start()
        monitor.complete("Done")
        assert monitor.is_running is False
        assert monitor.event_count == 2

    def test_error(self):
        monitor = CleanupMonitor()
        monitor.start()
        monitor.error("Something went wrong")
        assert monitor.event_count == 2

    def test_stop(self):
        monitor = CleanupMonitor()
        monitor.start()
        monitor.stop()
        assert monitor.is_running is False

    def test_elapsed(self):
        monitor = CleanupMonitor()
        monitor.start()
        assert monitor.elapsed >= 0

    def test_get_recent(self):
        monitor = CleanupMonitor()
        monitor.start()
        for i in range(20):
            monitor.progress(f"Step {i}")
        recent = monitor.get_recent(5)
        assert len(recent) == 5


class TestFormatMonitor:
    def test_idle(self):
        monitor = CleanupMonitor()
        text = format_monitor(monitor)
        assert "IDLE" in text

    def test_running(self):
        monitor = CleanupMonitor()
        monitor.start()
        text = format_monitor(monitor)
        assert "RUNNING" in text


class TestMonitorEvent:
    def test_defaults(self):
        event = MonitorEvent(timestamp=0, event_type="test", message="msg")
        assert event.data == {}
