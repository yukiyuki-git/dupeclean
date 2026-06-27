"""Tests for DupeClean result handler module."""

from __future__ import annotations

from dupeclean.result_handler import (
    ResultHandler,
    format_handler_summary,
)


class TestResultHandler:
    def test_handle_success(self):
        handler = ResultHandler()
        handler.handle({"success": True, "path": "/a"})
        assert handler.total == 1
        assert handler.successes == 1

    def test_handle_failure(self):
        handler = ResultHandler()
        handler.handle({"success": False, "path": "/a"})
        assert handler.failures == 1

    def test_success_callback(self):
        called = []
        handler = ResultHandler()
        handler.add_success_handler(lambda r: called.append(r))
        handler.handle({"success": True})
        assert len(called) == 1

    def test_failure_callback(self):
        called = []
        handler = ResultHandler()
        handler.add_failure_handler(lambda r: called.append(r))
        handler.handle({"success": False})
        assert len(called) == 1

    def test_callback_error_handling(self):
        handler = ResultHandler()
        handler.add_success_handler(lambda r: 1 / 0)  # Should not crash
        handler.handle({"success": True})
        assert handler.total == 1


class TestFormatHandlerSummary:
    def test_basic(self):
        handler = ResultHandler()
        handler.handle({"success": True})
        handler.handle({"success": False})
        text = format_handler_summary(handler)
        assert "2" in text
        assert "1" in text
