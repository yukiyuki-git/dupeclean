"""Tests for DupeClean cleanup runner module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.runner import (
    RunnerConfig,
    RunnerResult,
    format_runner_result,
    run_cleanup,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestRunCleanup:
    def test_dry_run(self):
        groups = [
            DuplicateGroup(
                group_id=0, hash_value="abc", file_size=100,
                files=[_fi("/a", 100), _fi("/b", 100), _fi("/c", 100)],
            )
        ]
        result = run_cleanup(groups)
        assert result.files_processed == 2
        assert result.files_deleted == 2
        assert result.space_freed == 200

    def test_empty_groups(self):
        result = run_cleanup([])
        assert result.files_processed == 0

    def test_single_file_group_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0, hash_value="abc", file_size=100,
                files=[_fi("/a")],
            )
        ]
        result = run_cleanup(groups)
        assert result.files_processed == 0


class TestRunnerConfig:
    def test_defaults(self):
        config = RunnerConfig()
        assert config.strategy == "shortest"
        assert config.dry_run is True


class TestRunnerResult:
    def test_freed_display(self):
        result = RunnerResult(space_freed=1024)
        assert "B" in result.freed_display

    def test_success_rate(self):
        result = RunnerResult(files_processed=10, files_deleted=8)
        assert result.success_rate == 0.8

    def test_zero_processed(self):
        result = RunnerResult()
        assert result.success_rate == 0.0


class TestFormatRunnerResult:
    def test_basic(self):
        result = RunnerResult(
            files_processed=10,
            files_deleted=8,
            space_freed=1000,
            duration=1.5,
        )
        text = format_runner_result(result)
        assert "10" in text
        assert "1.5s" in text
