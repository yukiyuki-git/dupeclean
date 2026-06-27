"""Tests for DupeClean error handling module."""

from __future__ import annotations

from dupeclean.error_handler import (
    DedupError,
    ErrorHandler,
    format_errors,
)


class TestErrorHandler:
    def test_add(self):
        handler = ErrorHandler()
        handler.add("test", "Test error")
        assert handler.count == 1

    def test_add_os_error(self):
        handler = ErrorHandler()
        handler.add_os_error(OSError("disk full"), "/test")
        assert handler.count == 1
        assert handler.errors[0].error_type == "os_error"

    def test_add_permission_error(self):
        handler = ErrorHandler()
        handler.add_permission_error("/protected/file")
        assert handler.count == 1
        assert handler.errors[0].recoverable is False

    def test_max_errors(self):
        handler = ErrorHandler(max_errors=5)
        for i in range(10):
            handler.add("test", f"Error {i}")
        assert handler.count == 5

    def test_recoverable_count(self):
        handler = ErrorHandler()
        handler.add("test", "rec", recoverable=True)
        handler.add("test", "crit", recoverable=False)
        assert handler.recoverable_count == 1

    def test_critical_count(self):
        handler = ErrorHandler()
        handler.add("test", "rec", recoverable=True)
        handler.add("test", "crit", recoverable=False)
        assert handler.critical_count == 1

    def test_has_critical(self):
        handler = ErrorHandler()
        assert handler.has_critical is False
        handler.add("test", "crit", recoverable=False)
        assert handler.has_critical is True

    def test_get_by_type(self):
        handler = ErrorHandler()
        handler.add("type_a", "error 1")
        handler.add("type_b", "error 2")
        handler.add("type_a", "error 3")
        assert len(handler.get_by_type("type_a")) == 2

    def test_clear(self):
        handler = ErrorHandler()
        handler.add("test", "error")
        handler.clear()
        assert handler.count == 0


class TestDedupError:
    def test_defaults(self):
        error = DedupError(error_type="test", message="msg")
        assert error.recoverable is True
        assert error.path == ""


class TestFormatErrors:
    def test_no_errors(self):
        handler = ErrorHandler()
        assert "No errors" in format_errors(handler)

    def test_with_errors(self):
        handler = ErrorHandler()
        handler.add("permission", "Access denied")
        handler.add("os_error", "Disk full")
        text = format_errors(handler)
        assert "permission" in text
        assert "os_error" in text
