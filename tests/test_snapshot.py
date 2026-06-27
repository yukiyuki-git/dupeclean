"""Tests for DupeClean snapshot module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.snapshot import (
    SnapshotDiff,
    create_snapshot,
    diff_snapshots,
    format_snapshot,
    format_snapshot_diff,
    load_snapshot,
    save_snapshot,
)


def _fi(path: str, size: int, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestCreateSnapshot:
    def test_basic(self):
        root = Path("/test")
        files = [
            _fi("/test/a.txt", 100, "h1"),
            _fi("/test/b.txt", 200, "h2"),
        ]
        snap = create_snapshot("test", root, files)
        assert snap.file_count == 2
        assert snap.total_size == 300

    def test_relative_paths(self):
        root = Path("/test")
        files = [_fi("/test/sub/file.txt", 100)]
        snap = create_snapshot("test", root, files)
        assert "sub/file.txt" in snap.files or "sub\\file.txt" in snap.files


class TestDiffSnapshots:
    def test_no_changes(self):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        old = create_snapshot("old", root, files)
        new = create_snapshot("new", root, files)
        diff = diff_snapshots(old, new)
        assert diff.unchanged == 1
        assert diff.total_changes == 0

    def test_added_files(self):
        root = Path("/test")
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        old = create_snapshot("old", root, old_files)
        new = create_snapshot("new", root, new_files)
        diff = diff_snapshots(old, new)
        assert len(diff.added) == 1

    def test_removed_files(self):
        root = Path("/test")
        old_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        new_files = [_fi("/test/a.txt", 100)]
        old = create_snapshot("old", root, old_files)
        new = create_snapshot("new", root, new_files)
        diff = diff_snapshots(old, new)
        assert len(diff.removed) == 1

    def test_modified_files(self):
        root = Path("/test")
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [_fi("/test/a.txt", 200)]
        old = create_snapshot("old", root, old_files)
        new = create_snapshot("new", root, new_files)
        diff = diff_snapshots(old, new)
        assert len(diff.modified) == 1


class TestSaveLoadSnapshot:
    def test_save_and_load(self, tmp_path):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        snap = create_snapshot("test", root, files)

        path = tmp_path / "snapshot.json"
        save_snapshot(snap, path)
        assert path.exists()

        loaded = load_snapshot(path)
        assert loaded is not None
        assert loaded.name == "test"
        assert loaded.file_count == 1

    def test_load_nonexistent(self, tmp_path):
        assert load_snapshot(tmp_path / "nope") is None


class TestFormatSnapshot:
    def test_contains_info(self):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        snap = create_snapshot("test", root, files)
        text = format_snapshot(snap)
        assert "test" in text
        assert "1" in text


class TestFormatSnapshotDiff:
    def test_with_changes(self):
        diff = SnapshotDiff(
            old_name="old",
            new_name="new",
            added=["new_file.txt"],
            removed=["old_file.txt"],
            modified=["changed.txt"],
            unchanged=10,
        )
        text = format_snapshot_diff(diff)
        assert "Added" in text
        assert "Removed" in text
        assert "Modified" in text
