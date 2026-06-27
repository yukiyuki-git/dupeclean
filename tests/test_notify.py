"""Tests for DupeClean notification module."""

from __future__ import annotations

from dupeclean.notify import (
    Notification,
    NotificationLog,
    format_notification,
    format_notification_log,
)


class TestNotification:
    def test_default_timestamp(self):
        n = Notification(title="Test", message="Hello")
        assert n.timestamp > 0

    def test_custom_level(self):
        n = Notification(title="Test", message="Hello", level="error")
        assert n.level == "error"


class TestNotificationLog:
    def test_add(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        log.info("Test", "Hello")
        assert len(log.notifications) == 1

    def test_info_warning_error(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        log.info("Test", "Info")
        log.warning("Test", "Warning")
        log.error("Test", "Error")
        log.success("Test", "Success")
        assert len(log.notifications) == 4

    def test_max_entries(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json", max_entries=5)
        for i in range(10):
            log.info(f"Test {i}", f"Message {i}")
        assert len(log.notifications) == 5

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "log.json"
        log = NotificationLog(path=path)
        log.info("Test", "Hello")
        log.save()
        assert path.exists()

        loaded = NotificationLog.load(path)
        assert len(loaded.notifications) == 1
        assert loaded.notifications[0].title == "Test"

    def test_load_nonexistent(self, tmp_path):
        log = NotificationLog.load(tmp_path / "nope")
        assert len(log.notifications) == 0

    def test_get_recent(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        for i in range(20):
            log.info(f"Test {i}", f"Message {i}")
        recent = log.get_recent(5)
        assert len(recent) == 5
        assert recent[0].title == "Test 15"

    def test_get_by_level(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        log.info("A", "info")
        log.warning("B", "warn")
        log.error("C", "error")
        log.info("D", "info")
        warnings = log.get_by_level("warning")
        assert len(warnings) == 1


class TestFormatNotification:
    def test_contains_title(self):
        n = Notification(
            title="Scan Complete",
            message="Found 100 files",
        )
        text = format_notification(n)
        assert "Scan Complete" in text

    def test_contains_level(self):
        n = Notification(title="Test", message="Hello", level="error")
        text = format_notification(n)
        assert "[X]" in text


class TestFormatNotificationLog:
    def test_empty(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        assert "No notifications" in format_notification_log(log)

    def test_with_notifications(self, tmp_path):
        log = NotificationLog(path=tmp_path / "log.json")
        log.info("Test", "Hello")
        log.warning("Warn", "Watch out")
        text = format_notification_log(log)
        assert "Test" in text
