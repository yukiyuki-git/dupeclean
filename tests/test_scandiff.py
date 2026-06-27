"""Tests for DupeClean scan diff module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.scandiff import (
    ScanSnapshot,
    diff_scans,
    format_diff,
)


def _fi(path: str, size: int, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestScanSnapshot:
    def test_from_files(self):
        root = Path("/test")
        files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        snap = ScanSnapshot.from_files(root, files, time.time())
        assert snap.file_count == 2
        assert snap.total_size == 300

    def test_empty_snapshot(self):
        snap = ScanSnapshot(root=Path("/test"), timestamp=time.time())
        assert snap.file_count == 0
        assert snap.total_size == 0


class TestDiffScans:
    def test_no_changes(self):
        files = [_fi("/test/a.txt", 100, 1.0)]
        old = ScanSnapshot.from_files(Path("/test"), files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), files, 2.0)
        diff = diff_scans(old, new)

        assert diff.total_changes == 0
        assert diff.unchanged == 1

    def test_added_files(self):
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert len(diff.added) == 1
        assert diff.added[0].path.name == "b.txt"

    def test_removed_files(self):
        old_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        new_files = [_fi("/test/a.txt", 100)]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert len(diff.removed) == 1
        assert diff.removed[0].path.name == "b.txt"

    def test_modified_files(self):
        old_files = [_fi("/test/a.txt", 100, 1.0)]
        new_files = [_fi("/test/a.txt", 200, 2.0)]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert len(diff.modified) == 1
        assert diff.modified[0][1].size == 200

    def test_size_change_grew(self):
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert diff.size_change == 200

    def test_size_change_shrank(self):
        old_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        new_files = [_fi("/test/a.txt", 100)]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert diff.size_change == -200

    def test_mixed_changes(self):
        old_files = [
            _fi("/test/a.txt", 100, 1.0),
            _fi("/test/b.txt", 200, 1.0),
            _fi("/test/c.txt", 300, 1.0),
        ]
        new_files = [
            _fi("/test/a.txt", 100, 1.0),  # unchanged
            _fi("/test/b.txt", 250, 2.0),  # modified
            _fi("/test/d.txt", 400, 2.0),  # added
        ]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)

        assert diff.unchanged == 1
        assert len(diff.modified) == 1
        assert len(diff.added) == 1
        assert len(diff.removed) == 1


class TestFormatDiff:
    def test_contains_summary(self):
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [
            _fi("/test/a.txt", 100),
            _fi("/test/b.txt", 200),
        ]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)
        text = format_diff(diff)

        assert "Added:" in text
        assert "Removed:" in text
        assert "Modified:" in text
        assert "Unchanged:" in text

    def test_shows_added_files(self):
        old_files = []
        new_files = [_fi("/test/big.bin", 1024 * 1024)]
        old = ScanSnapshot.from_files(Path("/test"), old_files, 1.0)
        new = ScanSnapshot.from_files(Path("/test"), new_files, 2.0)
        diff = diff_scans(old, new)
        text = format_diff(diff)

        assert "big.bin" in text
