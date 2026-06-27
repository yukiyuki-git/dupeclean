"""Tests for DupeClean strategy executor v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.strategy_executor_v2 import (
    StrategyResultV2,
    execute_strategy_v2,
    format_strategy_result_v2,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestExecuteStrategyV2:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b"), _fi("/c")],
            )
        ]
        result = execute_strategy_v2(groups)
        assert result.groups_processed == 1
        assert result.files_affected == 2
        assert result.space_saved == 200

    def test_empty_groups(self):
        result = execute_strategy_v2([])
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
        result = execute_strategy_v2(groups)
        assert result.files_affected == 0


class TestStrategyResultV2:
    def test_saved_display(self):
        result = StrategyResultV2(strategy_name="test", space_saved=1024)
        assert "B" in result.saved_display


class TestFormatStrategyResultV2:
    def test_basic(self):
        result = StrategyResultV2(
            strategy_name="shortest",
            groups_processed=5,
            files_affected=10,
            space_saved=1000,
        )
        text = format_strategy_result_v2(result)
        assert "shortest" in text
        assert "10" in text
