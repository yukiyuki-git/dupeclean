"""Tests for DupeClean rollback module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.rollback import (
    RollbackAction,
    RollbackManager,
    RollbackResult,
    format_rollback_result,
)


class TestRollbackManager:
    def test_add_action(self):
        manager = RollbackManager()
        manager.add_action(
            RollbackAction(
                action_type="restore",
                source=Path("/a"),
                backup=Path("/backup/a"),
            )
        )
        assert manager.action_count == 1

    def test_is_executed(self):
        manager = RollbackManager()
        assert manager.is_executed is False
        manager.execute()
        assert manager.is_executed is True

    def test_execute_empty(self):
        manager = RollbackManager()
        result = manager.execute()
        assert result.actions_attempted == 0

    def test_execute_with_missing_backup(self):
        manager = RollbackManager()
        manager.add_action(
            RollbackAction(
                action_type="restore",
                source=Path("/a"),
                backup=Path("/nonexistent/backup"),
            )
        )
        result = manager.execute()
        assert result.actions_failed == 1


class TestRollbackResult:
    def test_success_rate(self):
        result = RollbackResult(actions_attempted=10, actions_succeeded=8)
        assert result.success_rate == 0.8

    def test_zero_attempted(self):
        result = RollbackResult()
        assert result.success_rate == 0.0


class TestFormatRollbackResult:
    def test_basic(self):
        result = RollbackResult(actions_attempted=10, actions_succeeded=8)
        text = format_rollback_result(result)
        assert "8/10" in text
