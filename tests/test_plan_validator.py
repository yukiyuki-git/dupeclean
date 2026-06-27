"""Tests for DupeClean plan validator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.plan_validator import (
    PlanValidation,
    format_validation,
    validate_groups,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestValidateGroups:
    def test_valid_groups(self, tmp_path):
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
        validation = validate_groups(groups)
        assert validation.is_valid is True

    def test_single_file_group(self, tmp_path):
        a = tmp_path / "a.txt"
        a.write_bytes(b"alone")
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=5,
                files=[FileInfo.from_path(a)],
            )
        ]
        validation = validate_groups(groups)
        assert validation.warning_count >= 1

    def test_missing_file(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/nonexistent/a"), _fi("/nonexistent/b")],
            )
        ]
        validation = validate_groups(groups)
        assert validation.is_valid is False
        assert validation.error_count >= 1


class TestPlanValidation:
    def test_is_valid_default(self):
        validation = PlanValidation()
        assert validation.is_valid is True

    def test_add_error(self):
        validation = PlanValidation()
        validation.add_issue("error", "test error")
        assert validation.is_valid is False
        assert validation.error_count == 1

    def test_add_warning(self):
        validation = PlanValidation()
        validation.add_issue("warning", "test warning")
        assert validation.is_valid is True
        assert validation.warning_count == 1


class TestFormatValidation:
    def test_valid(self):
        validation = PlanValidation(groups_checked=5, files_checked=10)
        text = format_validation(validation)
        assert "VALID" in text

    def test_with_issues(self):
        validation = PlanValidation(groups_checked=1, files_checked=2)
        validation.add_issue("error", "File not found")
        text = format_validation(validation)
        assert "INVALID" in text
