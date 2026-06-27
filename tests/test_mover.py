"""Tests for DupeClean file mover module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.mover import (
    MoveAction,
    MoveResult,
    format_move_result,
    move_file,
    move_files,
)


class TestMoveFile:
    def test_move(self, tmp_path):
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest" / "source.txt"
        source.write_text("hello")
        action = move_file(source, dest)
        assert action.success is True
        assert dest.exists()
        assert not source.exists()

    def test_move_nonexistent(self, tmp_path):
        source = tmp_path / "nope.txt"
        dest = tmp_path / "dest" / "nope.txt"
        action = move_file(source, dest)
        assert action.success is False


class TestMoveFiles:
    def test_dry_run(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        dest = tmp_path / "dest"
        result = move_files(files, dest, dry_run=True)
        assert result.succeeded == 2
        assert all((tmp_path / f.path.name).exists() for f in files)

    def test_actual_move(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        dest = tmp_path / "dest"
        result = move_files(files, dest, dry_run=False)
        assert result.succeeded == 2
        assert (dest / "a.txt").exists()
        assert (dest / "b.txt").exists()


class TestMoveResult:
    def test_succeeded(self):
        result = MoveResult(
            actions=[
                MoveAction(source=Path("/a"), destination=Path("/b"), success=True),
                MoveAction(source=Path("/c"), destination=Path("/d"), success=False),
            ]
        )
        assert result.succeeded == 1
        assert result.failed == 1


class TestFormatMoveResult:
    def test_basic(self):
        result = MoveResult(
            actions=[
                MoveAction(source=Path("/a"), destination=Path("/b"), size=100, success=True),
            ]
        )
        text = format_move_result(result)
        assert "1" in text
