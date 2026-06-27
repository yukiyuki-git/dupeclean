"""Tests for DupeClean cleanup actions module."""

from __future__ import annotations

from dupeclean.cleanup_actions import (
    ActionResult,
    CleanupAction,
    CleanupExecutor,
    format_action_result,
    format_executor_stats,
)


class TestCleanupExecutor:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        executor = CleanupExecutor(dry_run=True)
        action = CleanupAction(
            action_type="delete",
            source=f,
        )
        result = executor.execute(action, file_size=5)
        assert result.success is True
        assert result.space_freed == 5
        assert f.exists()  # Not actually deleted

    def test_actual_delete(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        executor = CleanupExecutor(dry_run=False)
        action = CleanupAction(
            action_type="delete",
            source=f,
        )
        result = executor.execute(action, file_size=5)
        assert result.success is True
        assert not f.exists()

    def test_callbacks(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        before_called = []
        after_called = []

        def on_before(action):
            before_called.append(True)
            return True

        def on_after(action, success):
            after_called.append(success)

        executor = CleanupExecutor(
            dry_run=False,  # Use real mode to test after callback
            on_before=on_before,
            on_after=on_after,
        )
        action = CleanupAction(action_type="delete", source=f)
        executor.execute(action, file_size=5)
        assert len(before_called) == 1
        assert len(after_called) == 1

    def test_cancel_callback(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")

        executor = CleanupExecutor(
            dry_run=True,
            on_before=lambda a: False,
        )
        action = CleanupAction(action_type="delete", source=f)
        result = executor.execute(action)
        assert result.success is False

    def test_execute_batch(self, tmp_path):
        files = []
        for i in range(3):
            f = tmp_path / f"f{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)

        executor = CleanupExecutor(dry_run=True)
        actions = [(CleanupAction(action_type="delete", source=f), 100) for f in files]
        results = executor.execute_batch(actions)
        assert len(results) == 3
        assert executor.success_count == 3


class TestCleanupExecutorStats:
    def test_total_freed(self, tmp_path):
        executor = CleanupExecutor(dry_run=True)
        f = tmp_path / "f.txt"
        f.write_text("x")
        executor.execute(
            CleanupAction(action_type="delete", source=f),
            file_size=100,
        )
        assert executor.total_freed == 100


class TestFormatActionResult:
    def test_success(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        action = CleanupAction(action_type="delete", source=f)
        result = ActionResult(action=action, success=True)
        text = format_action_result(result)
        assert "OK" in text

    def test_failure(self, tmp_path):
        f = tmp_path / "file.txt"
        action = CleanupAction(action_type="delete", source=f)
        result = ActionResult(action=action, success=False)
        text = format_action_result(result)
        assert "FAILED" in text


class TestFormatExecutorStats:
    def test_basic(self, tmp_path):
        executor = CleanupExecutor(dry_run=True)
        text = format_executor_stats(executor)
        assert "Cleanup" in text
