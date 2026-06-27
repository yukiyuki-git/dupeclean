"""Tests for DupeClean notification module."""

from __future__ import annotations

from dupeclean.notification import (
    CleanupNotification,
    NotificationManager,
    format_notifications,
)


class TestNotificationManager:
    def test_notify(self):
        mgr = NotificationManager()
        mgr.notify("Test", "Hello")
        assert mgr.count == 1

    def test_success(self):
        mgr = NotificationManager()
        mgr.success("Done", "All good")
        assert mgr.count == 1
        assert mgr.notifications[0].level == "success"

    def test_warning(self):
        mgr = NotificationManager()
        mgr.warning("Watch", "Careful")
        assert mgr.count == 1

    def test_error(self):
        mgr = NotificationManager()
        mgr.error("Failed", "Bad")
        assert mgr.count == 1

    def test_max_notifications(self):
        mgr = NotificationManager(max_notifications=5)
        for i in range(10):
            mgr.notify(f"Test {i}", f"msg {i}")
        assert mgr.count <= 5

    def test_get_recent(self):
        mgr = NotificationManager()
        for i in range(20):
            mgr.notify(f"Test {i}", f"msg {i}")
        recent = mgr.get_recent(5)
        assert len(recent) == 5


class TestFormatNotifications:
    def test_empty(self):
        mgr = NotificationManager()
        assert "No notifications" in format_notifications(mgr)

    def test_with_notifications(self):
        mgr = NotificationManager()
        mgr.success("Done", "All good")
        text = format_notifications(mgr)
        assert "Done" in text


class TestCleanupNotification:
    def test_defaults(self):
        n = CleanupNotification(timestamp=0, title="test", message="msg")
        assert n.level == "info"
