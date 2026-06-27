"""Tests for DupeClean file validation module."""

from __future__ import annotations

from dupeclean.models import FileInfo
from dupeclean.validation import (
    ValidationReport,
    ValidationResult,
    check_file_integrity,
    format_validation_report,
    validate_file,
    validate_files,
)


class TestValidateFile:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "valid.txt"
        f.write_text("hello")
        result = validate_file(f)
        assert result.is_valid is True
        assert result.size == 5

    def test_nonexistent(self, tmp_path):
        result = validate_file(tmp_path / "nope")
        assert result.is_valid is False
        assert "not found" in result.issues[0].lower()

    def test_zero_size(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        result = validate_file(f)
        assert result.is_valid is True
        assert result.size == 0


class TestValidateFiles:
    def test_all_valid(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            p = tmp_path / name
            p.write_text("content")
            fi = FileInfo.from_path(p)
            if fi:
                files.append(fi)

        report = validate_files(files)
        assert report.is_clean is True
        assert report.valid_files == 2

    def test_with_invalid(self, tmp_path):
        files = []
        # Valid file
        p = tmp_path / "valid.txt"
        p.write_text("content")
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)

        # Invalid file (deleted after creation)
        p2 = tmp_path / "deleted.txt"
        p2.write_text("temp")
        fi2 = FileInfo.from_path(p2)
        p2.unlink()  # Delete it
        if fi2:
            files.append(fi2)

        report = validate_files(files)
        assert report.invalid_files >= 1


class TestCheckFileIntegrity:
    def test_matching_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        import hashlib

        expected = hashlib.sha256(b"hello").hexdigest()
        assert check_file_integrity(f, expected) is True

    def test_non_matching_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert check_file_integrity(f, "wrong_hash") is False

    def test_nonexistent(self, tmp_path):
        assert check_file_integrity(tmp_path / "nope", "abc") is False


class TestValidationReport:
    def test_is_clean(self):
        report = ValidationReport(total_files=10, valid_files=10, invalid_files=0)
        assert report.is_clean is True

    def test_not_clean(self):
        report = ValidationReport(total_files=10, valid_files=8, invalid_files=2)
        assert report.is_clean is False

    def test_error_rate(self):
        report = ValidationReport(total_files=10, valid_files=8, invalid_files=2)
        assert report.error_rate == 0.2


class TestFormatValidationReport:
    def test_clean_report(self):
        report = ValidationReport(total_files=10, valid_files=10, invalid_files=0)
        text = format_validation_report(report)
        assert "valid" in text.lower()

    def test_report_with_errors(self, tmp_path):
        report = ValidationReport(
            total_files=2,
            valid_files=1,
            invalid_files=1,
            results=[
                ValidationResult(
                    path=tmp_path / "bad.txt",
                    is_valid=False,
                    issues=["Read error"],
                ),
            ],
        )
        text = format_validation_report(report)
        assert "invalid" in text.lower() or "error" in text.lower()
