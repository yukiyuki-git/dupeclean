"""Tests for DupeClean file rename module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.file_rename import (
    RenameAction,
    RenamePlan,
    execute_rename,
    format_rename_plan,
    rename_lowercase,
    rename_replace,
    rename_sequential,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestRenameSequential:
    def test_basic(self):
        files = [_fi("/test/a.txt"), _fi("/test/b.txt"), _fi("/test/c.txt")]
        plan = rename_sequential(files)
        assert plan.count == 3


class TestRenameReplace:
    def test_basic(self):
        files = [_fi("/test/photo (1).jpg"), _fi("/test/photo copy.jpg")]
        plan = rename_replace(files, " (1)", "")
        assert plan.count == 1


class TestRenameLowercase:
    def test_basic(self):
        files = [_fi("/test/README.MD"), _fi("/test/Photo.JPG")]
        plan = rename_lowercase(files)
        assert plan.count == 2


class TestExecuteRename:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        files = [FileInfo.from_path(f)]
        plan = rename_sequential(files)
        result = execute_rename(plan, dry_run=True)
        assert result["succeeded"] == 1

    def test_actual_rename(self, tmp_path):
        f = tmp_path / "FILE.TXT"
        f.write_text("x")
        files = [FileInfo.from_path(f)]
        plan = rename_lowercase(files)
        result = execute_rename(plan, dry_run=False)
        assert result["succeeded"] == 1


class TestRenamePlan:
    def test_count(self):
        plan = RenamePlan(actions=[RenameAction(Path("/a"), Path("/b"))])
        assert plan.count == 1


class TestFormatRenamePlan:
    def test_empty(self):
        plan = RenamePlan()
        assert "No renames" in format_rename_plan(plan)

    def test_with_actions(self):
        files = [_fi("/test/photo (1).jpg")]
        plan = rename_replace(files, " (1)", "")
        text = format_rename_plan(plan)
        assert "photo" in text
