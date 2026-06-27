"""Tests for DupeClean file rename module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.rename import (
    RenameAction,
    RenamePlan,
    execute_rename,
    format_rename_plan,
    rename_add_prefix,
    rename_add_suffix,
    rename_lowercase,
    rename_replace,
    rename_sequential,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestRenameSequential:
    def test_basic(self):
        files = [
            _fi("/test/a.txt"),
            _fi("/test/b.txt"),
            _fi("/test/c.txt"),
        ]
        plan = rename_sequential(files)
        assert plan.count == 3

    def test_custom_pattern(self):
        files = [_fi("/test/photo.jpg"), _fi("/test/image.png")]
        plan = rename_sequential(files, pattern="{index}_{original}{ext}")
        assert plan.count == 2


class TestRenameReplace:
    def test_basic(self):
        files = [
            _fi("/test/photo (1).jpg"),
            _fi("/test/photo copy.jpg"),
        ]
        plan = rename_replace(files, " (1)", "")
        assert plan.count == 1  # Only first file matches

    def test_multiple_matches(self):
        files = [
            _fi("/test/file_v1.txt"),
            _fi("/test/other_v1.txt"),
        ]
        plan = rename_replace(files, "_v1", "_v2")
        assert plan.count == 2

    def test_no_match(self):
        files = [_fi("/test/normal.txt")]
        plan = rename_replace(files, "XYZ", "ABC")
        assert plan.count == 0


class TestRenameLowercase:
    def test_basic(self):
        files = [
            _fi("/test/README.MD"),
            _fi("/test/Photo.JPG"),
        ]
        plan = rename_lowercase(files)
        assert plan.count == 2


class TestRenameAddPrefix:
    def test_basic(self):
        files = [_fi("/test/file.txt")]
        plan = rename_add_prefix(files, "backup_")
        assert plan.count == 1
        assert plan.actions[0].new_path.name == "backup_file.txt"


class TestRenameAddSuffix:
    def test_basic(self):
        files = [_fi("/test/file.txt")]
        plan = rename_add_suffix(files, "_v2")
        assert plan.count == 1
        assert plan.actions[0].new_path.name == "file_v2.txt"


class TestExecuteRename:
    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        files = [FileInfo.from_path(f)]
        plan = rename_add_prefix(files, "new_")
        result = execute_rename(plan, dry_run=True)
        assert result["succeeded"] == 1
        assert f.exists()  # Not renamed in dry run

    def test_actual_rename(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        files = [FileInfo.from_path(f)]
        plan = rename_add_prefix(files, "new_")
        result = execute_rename(plan, dry_run=False)
        assert result["succeeded"] == 1
        assert not f.exists()
        assert (tmp_path / "new_file.txt").exists()


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
