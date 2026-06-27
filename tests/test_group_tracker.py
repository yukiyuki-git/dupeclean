"""Tests for DupeClean group tracker module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_tracker import (
    GroupSnapshot,
    GroupTracker,
    format_tracker,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestGroupTracker:
    def test_snapshot(self):
        tracker = GroupTracker()
        tracker.snapshot([_group(0, 100, 3)])
        assert tracker.snapshot_count == 1

    def test_multiple_snapshots(self):
        tracker = GroupTracker()
        tracker.snapshot([_group(0, 100, 3)])
        tracker.snapshot([_group(0, 100, 3), _group(1, 200, 2)])
        assert tracker.snapshot_count == 2

    def test_get_latest(self):
        tracker = GroupTracker()
        tracker.snapshot([_group(0, 100, 3)])
        latest = tracker.get_latest()
        assert latest is not None
        assert latest.group_count == 1

    def test_get_trend_worsening(self):
        tracker = GroupTracker()
        tracker.snapshots.append(GroupSnapshot(timestamp=0, group_count=1, total_wasted=100))
        tracker.snapshots.append(GroupSnapshot(timestamp=1, group_count=2, total_wasted=200))
        assert tracker.get_trend() == "Worsening"

    def test_get_trend_improving(self):
        tracker = GroupTracker()
        tracker.snapshots.append(GroupSnapshot(timestamp=0, group_count=2, total_wasted=200))
        tracker.snapshots.append(GroupSnapshot(timestamp=1, group_count=1, total_wasted=100))
        assert tracker.get_trend() == "Improving"

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "tracker.json"
        tracker = GroupTracker()
        tracker.snapshot([_group(0, 100, 3)])
        tracker.save(path)
        assert path.exists()
        loaded = GroupTracker.load(path)
        assert loaded.snapshot_count == 1

    def test_load_nonexistent(self, tmp_path):
        tracker = GroupTracker.load(tmp_path / "nope")
        assert tracker.snapshot_count == 0


class TestFormatTracker:
    def test_empty(self):
        tracker = GroupTracker()
        assert "No snapshots" in format_tracker(tracker)

    def test_with_snapshots(self):
        tracker = GroupTracker()
        tracker.snapshot([_group(0, 100, 3)])
        text = format_tracker(tracker)
        assert "1" in text
