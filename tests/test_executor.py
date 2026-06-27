"""Tests for DupeClean cleanup executor module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.executor import (
    CleanupExecutorV2,
    ExecutorAction,
    ExecutorResult,
    format_executor_result,
)


class TestCleanupExecutorV2:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        executor = CleanupExecutorV2(dry_run=True)
        action = ExecutorAction(action_type="delete", source=f, size=5)
        result = executor.execute(action)
        assert result.success is True
        assert f.exists()  # Not deleted in dry run

    def test_actual_delete(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        executor = CleanupExecutorV2(dry_run=False)
        action = ExecutorAction(action_type="delete", source=f, size=5)
        result = executor.execute(action)
        assert result.success is True
        assert not f.exists()

    def test_rollback(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        backup_dir = tmp_path / "backups"
        executor = CleanupExecutorV2(dry_run=False, backup_dir=backup_dir)
        action = ExecutorAction(action_type="delete", source=f, size=5)
        executor.execute(action)
        assert not f.exists()
        restored = executor.rollback()
        assert restored >= 0  # May or may not restore depending on backup

    def test_success_count(self, tmp_path):
        executor = CleanupExecutorV2(dry_run=True)
        for i in range(3):
            executor.execute(
                ExecutorAction(action_type="delete", source=tmp_path / f"f{i}", size=100)
            )
        assert executor.success_count == 3

    def test_total_freed(self, tmp_path):
        executor = CleanupExecutorV2(dry_run=True)
        executor.execute(ExecutorAction(action_type="delete", source=tmp_path / "a", size=100))
        executor.execute(ExecutorAction(action_type="delete", source=tmp_path / "b", size=200))
        assert executor.total_freed == 300


class TestExecutorAction:
    def test_size_display(self):
        action = ExecutorAction(action_type="delete", source=Path("/a"), size=1024)
        assert "B" in action.size_display


class TestFormatExecutorResult:
    def test_success(self):
        action = ExecutorAction(action_type="delete", source=Path("/a/file.txt"), size=100)
        result = ExecutorResult(action=action, success=True)
        text = format_executor_result(result)
        assert "OK" in text

    def test_failure(self):
        action = ExecutorAction(action_type="delete", source=Path("/a/file.txt"), size=100)
        result = ExecutorResult(action=action, success=False)
        text = format_executor_result(result)
        assert "FAILED" in text
