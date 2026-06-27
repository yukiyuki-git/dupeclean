"""Tests for DupeClean file validator module."""

from __future__ import annotations

from dupeclean.file_validator import (
    format_validation_results,
    validate_file,
    validate_files,
)
from dupeclean.models import FileInfo


class TestValidateFile:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "valid.txt"
        f.write_text("hello")
        fi = FileInfo.from_path(f)
        assert fi is not None
        result = validate_file(fi)
        assert result.is_valid is True

    def test_nonexistent_file(self, tmp_path):
        fi = FileInfo(path=tmp_path / "nope.txt", size=100, mtime=0)
        result = validate_file(fi)
        assert result.is_valid is False
        assert "not found" in result.issues[0].lower()

    def test_zero_size_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        fi = FileInfo.from_path(f)
        assert fi is not None
        result = validate_file(fi)
        assert result.is_valid is True


class TestValidateFiles:
    def test_all_valid(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        results = validate_files(files)
        assert all(r.is_valid for r in results)


class TestValidationResult:
    def test_size_display(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"x" * 1024)
        fi = FileInfo.from_path(f)
        assert fi is not None
        result = validate_file(fi)
        assert "B" in result.size_display


class TestFormatValidationResults:
    def test_all_valid(self, tmp_path):
        f = tmp_path / "valid.txt"
        f.write_text("hello")
        fi = FileInfo.from_path(f)
        assert fi is not None
        results = [validate_file(fi)]
        text = format_validation_results(results)
        assert "Valid:" in text

    def test_with_invalid(self, tmp_path):
        fi = FileInfo(path=tmp_path / "nope.txt", size=100, mtime=0)
        results = [validate_file(fi)]
        text = format_validation_results(results)
        assert "Invalid:" in text
