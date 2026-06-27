"""Tests for DupeClean strategy executor module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.strategy_executor import (
    StrategyExecution,
    execute_strategy,
    format_execution,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestExecuteStrategy:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b"), _fi("/c")],
            )
        ]
        result = execute_strategy(groups)
        assert result.groups_processed == 1
        assert result.files_removed == 2
        assert result.space_freed == 200

    def test_empty_groups(self):
        result = execute_strategy([])
        assert result.groups_processed == 0

    def test_single_file_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a")],
            )
        ]
        result = execute_strategy(groups)
        assert result.files_processed == 0


class TestStrategyExecution:
    def test_freed_display(self):
        execution = StrategyExecution(strategy_name="test", space_freed=1024)
        assert "B" in execution.freed_display

    def test_success_rate(self):
        execution = StrategyExecution(
            strategy_name="test",
            files_processed=10,
            files_kept=3,
            files_removed=7,
        )
        assert execution.success_rate == 1.0


class TestFormatExecution:
    def test_basic(self):
        execution = StrategyExecution(
            strategy_name="shortest",
            groups_processed=5,
            files_removed=10,
            space_freed=1000,
        )
        text = format_execution(execution)
        assert "shortest" in text
        assert "10" in text
