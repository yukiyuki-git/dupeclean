"""Tests for DupeClean group validator v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_validator_v2 import (
    GroupValidationV2,
    ValidationCheck,
    ValidationReportV2,
    format_validation_v2,
    validate_group_v2,
    validate_groups_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestValidateGroupV2:
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
        result = validate_group_v2(group)
        assert result.is_valid is True

    def test_single_file(self, tmp_path):
        a = tmp_path / "a.txt"
        a.write_bytes(b"alone")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=5,
            files=[FileInfo.from_path(a)],
        )
        result = validate_group_v2(group)
        assert result.is_valid is False

    def test_missing_file(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/nonexistent/a"), _fi("/nonexistent/b")],
        )
        result = validate_group_v2(group)
        assert result.is_valid is False


class TestValidateGroupsV2:
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
        report = validate_groups_v2(groups)
        assert report.is_clean is True


class TestValidationReportV2:
    def test_validity_rate(self):
        report = ValidationReportV2(groups_checked=10, groups_valid=8)
        assert report.validity_rate == 0.8


class TestFormatValidationV2:
    def test_clean(self, tmp_path):
        report = ValidationReportV2(groups_checked=5, groups_valid=5)
        text = format_validation_v2(report)
        assert "100.0%" in text


class TestGroupValidationV2:
    def test_failed_checks(self):
        validation = GroupValidationV2(
            group_id=0,
            checks=[
                ValidationCheck(check_name="test", passed=True),
                ValidationCheck(check_name="test2", passed=False),
            ],
        )
        assert len(validation.failed_checks) == 1
