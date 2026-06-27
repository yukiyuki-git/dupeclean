"""Tests for DupeClean cleanup validator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.cleanup_validator import (
    CleanupValidation,
    CleanupValidationReport,
    format_cleanup_validation,
    validate_cleanup,
    validate_cleanup_all,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestValidateCleanup:
    def test_valid_group(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=4,
            files=[FileInfo.from_path(a), FileInfo.from_path(b)],
        )
        result = validate_cleanup(group)
        assert result.is_valid is True

    def test_missing_file(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/nonexistent/a"), _fi("/nonexistent/b")],
        )
        result = validate_cleanup(group)
        assert result.is_valid is False


class TestValidateCleanupAll:
    def test_all_valid(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=4,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        report = validate_cleanup_all(groups)
        assert report.is_clean is True


class TestCleanupValidation:
    def test_issue_count(self):
        validation = CleanupValidation(group_id=0, is_valid=False, issues=["error 1", "error 2"])
        assert validation.issue_count == 2


class TestFormatCleanupValidation:
    def test_clean(self):
        report = CleanupValidationReport(groups_checked=5, groups_valid=5)
        text = format_cleanup_validation(report)
        assert "100.0%" in text
