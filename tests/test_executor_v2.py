"""Tests for DupeClean executor v2 module."""

from __future__ import annotations

from dupeclean.executor_v2 import (
    ExecutionRecord,
    ExecutorConfig,
    ExecutorV2,
    format_executor_v2,
)


class TestExecutorV2:
    def test_execute_dry_run(self):
        executor = ExecutorV2(config=ExecutorConfig(dry_run=True))
        record = executor.execute("/a.txt", "delete", 100)
        assert record.success is True
        assert executor.total_records == 1

    def test_multiple_executions(self):
        executor = ExecutorV2()
        executor.execute("/a", "delete", 100)
        executor.execute("/b", "hardlink", 200)
        assert executor.total_records == 2

    def test_success_count(self):
        executor = ExecutorV2()
        executor.execute("/a", "delete", 100)
        assert executor.success_count == 1

    def test_total_freed(self):
        executor = ExecutorV2()
        executor.execute("/a", "delete", 100)
        executor.execute("/b", "delete", 200)
        assert executor.total_freed == 300


class TestExecutorConfig:
    def test_defaults(self):
        config = ExecutorConfig()
        assert config.dry_run is True
        assert config.verify is True


class TestExecutionRecord:
    def test_size_display(self):
        record = ExecutionRecord(path="/a", action="delete", success=True, size=1024)
        assert "B" in record.size_display


class TestFormatExecutorV2:
    def test_basic(self):
        executor = ExecutorV2()
        executor.execute("/a", "delete", 100)
        text = format_executor_v2(executor)
        assert "1 actions" in text
