"""Tests for DupeClean file copier module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.copier import (
    CopyAction,
    CopyResult,
    copy_file,
    copy_files,
    format_copy_result,
)
from dupeclean.models import FileInfo


class TestCopyFile:
    def test_copy(self, tmp_path):
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest" / "source.txt"
        source.write_text("hello")
        action = copy_file(source, dest)
        assert action.success is True
        assert dest.exists()
        assert source.exists()  # Source preserved

    def test_copy_nonexistent(self, tmp_path):
        source = tmp_path / "nope.txt"
        dest = tmp_path / "dest" / "nope.txt"
        action = copy_file(source, dest)
        assert action.success is False


class TestCopyFiles:
    def test_dry_run(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        dest = tmp_path / "dest"
        result = copy_files(files, dest, dry_run=True)
        assert result.succeeded == 2

    def test_actual_copy(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        dest = tmp_path / "dest"
        result = copy_files(files, dest, dry_run=False)
        assert result.succeeded == 2
        assert (dest / "a.txt").exists()
        assert (tmp_path / "a.txt").exists()  # Original preserved


class TestCopyResult:
    def test_succeeded(self):
        result = CopyResult(
            actions=[
                CopyAction(source=Path("/a"), destination=Path("/b"), success=True),
                CopyAction(source=Path("/c"), destination=Path("/d"), success=False),
            ]
        )
        assert result.succeeded == 1
        assert result.failed == 1


class TestFormatCopyResult:
    def test_basic(self):
        result = CopyResult(
            actions=[
                CopyAction(source=Path("/a"), destination=Path("/b"), size=100, success=True),
            ]
        )
        text = format_copy_result(result)
        assert "1" in text
