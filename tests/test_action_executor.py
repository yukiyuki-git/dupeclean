"""Tests for DupeClean action executor module."""

from __future__ import annotations

from dupeclean.action_executor import (
    ActionConfig,
    ActionExecutor,
    ActionResult,
    format_action_result,
)


class TestActionExecutor:
    def test_execute(self):
        executor = ActionExecutor()
        result = executor.execute("/a.txt", "delete", 100)
        assert result.success is True
        assert executor.total == 1

    def test_multiple_executions(self):
        executor = ActionExecutor()
        executor.execute("/a", "delete", 100)
        executor.execute("/b", "hardlink", 200)
        assert executor.total == 2

    def test_successes(self):
        executor = ActionExecutor()
        executor.execute("/a", "delete", 100)
        assert executor.successes == 1


class TestActionConfig:
    def test_defaults(self):
        config = ActionConfig()
        assert config.dry_run is True


class TestActionResult:
    def test_size_display(self):
        result = ActionResult(success=True, path="/a", action="delete", size=1024)
        assert "B" in result.size_display


class TestFormatActionResult:
    def test_success(self):
        result = ActionResult(success=True, path="/a/file.txt", action="delete", size=100)
        text = format_action_result(result)
        assert "OK" in text

    def test_failure(self):
        result = ActionResult(success=False, path="/a/file.txt", action="delete", size=100)
        text = format_action_result(result)
        assert "FAILED" in text
