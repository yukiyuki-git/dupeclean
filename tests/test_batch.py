"""Tests for DupeClean batch file operations module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.batch import (
    BatchResult,
    batch_copy,
    batch_delete,
    batch_move,
    batch_rename,
    format_batch_result,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestBatchMove:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        dest = tmp_path / "dest"

        files = [FileInfo.from_path(f)]
        result = batch_move(files, dest, dry_run=True)
        assert result.succeeded == 1
        assert f.exists()  # Not moved in dry run

    def test_actual_move(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        dest = tmp_path / "dest"

        files = [FileInfo.from_path(f)]
        result = batch_move(files, dest, dry_run=False)
        assert result.succeeded == 1
        assert not f.exists()
        assert (dest / "file.txt").exists()

    def test_name_conflict(self, tmp_path):
        f1 = tmp_path / "file.txt"
        f2 = tmp_path / "other.txt"
        f1.write_text("a")
        f2.write_text("b")
        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "file.txt").write_text("existing")

        files = [FileInfo.from_path(f1)]
        result = batch_move(files, dest, dry_run=False)
        assert result.succeeded == 1


class TestBatchCopy:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        dest = tmp_path / "dest"

        files = [FileInfo.from_path(f)]
        result = batch_copy(files, dest, dry_run=True)
        assert result.succeeded == 1

    def test_actual_copy(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        dest = tmp_path / "dest"

        files = [FileInfo.from_path(f)]
        result = batch_copy(files, dest, dry_run=False)
        assert result.succeeded == 1
        assert f.exists()  # Original still there
        assert (dest / "file.txt").exists()


class TestBatchDelete:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")

        files = [FileInfo.from_path(f)]
        result = batch_delete(files, dry_run=True)
        assert result.succeeded == 1
        assert f.exists()

    def test_actual_delete(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")

        files = [FileInfo.from_path(f)]
        result = batch_delete(files, dry_run=False)
        assert result.succeeded == 1
        assert not f.exists()


class TestBatchRename:
    def test_rename(self, tmp_path):
        f = tmp_path / "photo (1).jpg"
        f.write_bytes(b"x")

        files = [FileInfo.from_path(f)]
        result = batch_rename(files, " (1)", "", dry_run=False)
        assert result.succeeded == 1
        assert (tmp_path / "photo.jpg").exists()

    def test_no_match(self, tmp_path):
        f = tmp_path / "normal.txt"
        f.write_text("x")

        files = [FileInfo.from_path(f)]
        result = batch_rename(files, "XYZ", "ABC", dry_run=False)
        assert result.skipped == 1


class TestBatchResult:
    def test_success_rate(self):
        result = BatchResult(action_type="test", total=10, succeeded=8)
        assert result.success_rate == 80.0

    def test_zero_total(self):
        result = BatchResult(action_type="test")
        assert result.success_rate == 0.0

    def test_bytes_display(self):
        result = BatchResult(action_type="test", bytes_processed=1024)
        assert "B" in result.bytes_display


class TestFormatBatchResult:
    def test_contains_stats(self):
        result = BatchResult(
            action_type="move",
            total=10,
            succeeded=8,
            failed=2,
        )
        text = format_batch_result(result)
        assert "move" in text
        assert "10" in text
        assert "8" in text

    def test_with_errors(self):
        result = BatchResult(
            action_type="delete",
            total=1,
            failed=1,
            errors=["Permission denied"],
        )
        text = format_batch_result(result)
        assert "Permission denied" in text
