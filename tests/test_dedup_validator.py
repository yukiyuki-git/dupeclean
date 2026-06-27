"""Tests for DupeClean dedup validator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_validator import (
    ValidationSummary,
    format_validation_summary,
    validate_group,
    validate_groups,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestValidateGroup:
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
        result = validate_group(group)
        assert result.is_valid is True
        assert result.file_count == 2

    def test_single_file_group(self, tmp_path):
        a = tmp_path / "a.txt"
        a.write_bytes(b"alone")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=5,
            files=[FileInfo.from_path(a)],
        )
        result = validate_group(group)
        assert result.is_valid is False
        assert "only 1" in result.issues[0]

    def test_missing_file(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/nonexistent/a"), _fi("/nonexistent/b")],
        )
        result = validate_group(group)
        assert result.is_valid is False


class TestValidateGroups:
    def test_all_valid(self, tmp_path):
        groups = []
        for i in range(2):
            a = tmp_path / f"a{i}.txt"
            b = tmp_path / f"b{i}.txt"
            a.write_bytes(b"same")
            b.write_bytes(b"same")
            groups.append(
                DuplicateGroup(
                    group_id=i,
                    hash_value=f"h{i}",
                    file_size=4,
                    files=[
                        FileInfo.from_path(a),
                        FileInfo.from_path(b),
                    ],
                )
            )
        summary = validate_groups(groups)
        assert summary.is_clean is True
        assert summary.valid_groups == 2

    def test_empty_groups(self):
        summary = validate_groups([])
        assert summary.is_clean is True


class TestValidationSummary:
    def test_validity_rate(self):
        summary = ValidationSummary(total_groups=10, valid_groups=8, invalid_groups=2)
        assert summary.validity_rate == 0.8

    def test_is_clean(self):
        summary = ValidationSummary(total_groups=5, valid_groups=5)
        assert summary.is_clean is True


class TestFormatValidationSummary:
    def test_clean(self, tmp_path):
        summary = ValidationSummary(total_groups=5, valid_groups=5, total_files=10)
        text = format_validation_summary(summary)
        assert "valid" in text.lower()

    def test_with_issues(self):
        summary = ValidationSummary(
            total_groups=2,
            valid_groups=1,
            invalid_groups=1,
            issues=["Missing file"],
        )
        text = format_validation_summary(summary)
        assert "Missing" in text
