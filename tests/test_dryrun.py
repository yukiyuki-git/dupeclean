"""Tests for DupeClean dry-run module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dryrun import (
    DryRunResult,
    format_dry_run,
    preview_cleanup,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=[_fi("/a/file.txt"), _fi("/b/file.txt"), _fi("/c/file.txt")],
        ),
        DuplicateGroup(
            group_id=1,
            hash_value="def",
            file_size=2000,
            files=[_fi("/d/data.bin"), _fi("/e/data.bin")],
        ),
    ]


class TestPreviewCleanup:
    def test_basic(self):
        groups = _make_groups()
        result = preview_cleanup(groups)
        assert result.total_actions == 3  # 2 + 1
        assert result.total_savings > 0

    def test_empty_groups(self):
        result = preview_cleanup([])
        assert result.total_actions == 0

    def test_single_file_groups_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a")],
            )
        ]
        result = preview_cleanup(groups)
        assert result.total_actions == 0


class TestDryRunResult:
    def test_savings_display(self):
        result = DryRunResult(total_savings=1024)
        assert "B" in result.savings_display


class TestFormatDryRun:
    def test_empty(self):
        result = DryRunResult()
        assert "No actions" in format_dry_run(result)

    def test_with_actions(self):
        groups = _make_groups()
        result = preview_cleanup(groups)
        text = format_dry_run(result)
        assert "delete" in text
        assert "Duplicate" in text or "file" in text
