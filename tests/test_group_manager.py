"""Tests for DupeClean group manager module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_manager import (
    GroupManager,
    format_group_manager,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int, ext: str = ".txt") -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}{ext}", size) for i in range(count)],
    )


class TestGroupManager:
    def test_add(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        assert mgr.count == 1

    def test_remove(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        assert mgr.remove(0) is True
        assert mgr.count == 0

    def test_remove_nonexistent(self):
        mgr = GroupManager()
        assert mgr.remove(99) is False

    def test_get(self):
        mgr = GroupManager()
        mgr.add(_group(5, 100, 2))
        assert mgr.get(5) is not None
        assert mgr.get(99) is None

    def test_total_files(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 3))
        mgr.add(_group(1, 200, 2))
        assert mgr.total_files == 5

    def test_total_wasted(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 3))  # 200 wasted
        mgr.add(_group(1, 200, 2))  # 200 wasted
        assert mgr.total_wasted == 400

    def test_sort_by_size(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        mgr.add(_group(1, 1000, 2))
        mgr.sort_by_size()
        assert mgr.groups[0].file_size == 1000

    def test_sort_by_waste(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))  # 100 wasted
        mgr.add(_group(1, 100, 5))  # 400 wasted
        mgr.sort_by_waste()
        assert mgr.groups[0].count == 5

    def test_sort_by_count(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        mgr.add(_group(1, 100, 5))
        mgr.sort_by_count()
        assert mgr.groups[0].count == 5

    def test_filter_by_min_size(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        mgr.add(_group(1, 1000, 2))
        filtered = mgr.filter_by_min_size(500)
        assert len(filtered) == 1

    def test_filter_by_extension(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2, ".txt"))
        mgr.add(_group(1, 200, 2, ".py"))
        filtered = mgr.filter_by_extension(".txt")
        assert len(filtered) == 1


class TestFormatGroupManager:
    def test_basic(self):
        mgr = GroupManager()
        mgr.add(_group(0, 100, 2))
        text = format_group_manager(mgr)
        assert "1" in text
