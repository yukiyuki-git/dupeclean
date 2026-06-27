"""Tests for DupeClean event module."""

from __future__ import annotations

from dupeclean.events import (
    CleanupEvent,
    EventManager,
    format_events,
)


class TestEventManager:
    def test_emit(self):
        mgr = EventManager()
        mgr.emit("test", message="hello")
        assert mgr.count == 1

    def test_success(self):
        mgr = EventManager()
        mgr.success("Done")
        assert mgr.count == 1
        assert mgr.events[0].event_type == "success"

    def test_error(self):
        mgr = EventManager()
        mgr.error("Failed")
        assert mgr.count == 1

    def test_info(self):
        mgr = EventManager()
        mgr.info("Info message")
        assert mgr.count == 1

    def test_max_events(self):
        mgr = EventManager(max_events=5)
        for i in range(10):
            mgr.emit("test", message=f"msg {i}")
        assert mgr.count <= 5

    def test_get_recent(self):
        mgr = EventManager()
        for i in range(20):
            mgr.emit("test", message=f"msg {i}")
        recent = mgr.get_recent(5)
        assert len(recent) == 5

    def test_get_by_type(self):
        mgr = EventManager()
        mgr.emit("error", message="e")
        mgr.emit("success", message="s")
        mgr.emit("error", message="e2")
        assert len(mgr.get_by_type("error")) == 2


class TestCleanupEvent:
    def test_is_error(self):
        event = CleanupEvent(event_type="error", timestamp=0)
        assert event.is_error is True

    def test_is_success(self):
        event = CleanupEvent(event_type="success", timestamp=0)
        assert event.is_success is True


class TestFormatEvents:
    def test_empty(self):
        mgr = EventManager()
        assert "No events" in format_events(mgr)

    def test_with_events(self):
        mgr = EventManager()
        mgr.success("Done")
        text = format_events(mgr)
        assert "success" in text
