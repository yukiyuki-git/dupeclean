"""Tests for DupeClean group comparator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_comparator import (
    GroupDiff,
    compare_groups,
    format_group_diff,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, hash_val: str, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=hash_val,
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestCompareGroups:
    def test_no_changes(self):
        old = [_group(0, "abc", 100, 2)]
        new = [_group(0, "abc", 100, 2)]
        diff = compare_groups(old, new)
        assert diff.unchanged == 1
        assert diff.total_changes == 0

    def test_added_groups(self):
        old = [_group(0, "abc", 100, 2)]
        new = [_group(0, "abc", 100, 2), _group(1, "def", 200, 3)]
        diff = compare_groups(old, new)
        assert len(diff.added) == 1
        assert diff.net_change == 1

    def test_removed_groups(self):
        old = [_group(0, "abc", 100, 2), _group(1, "def", 200, 3)]
        new = [_group(0, "abc", 100, 2)]
        diff = compare_groups(old, new)
        assert len(diff.removed) == 1
        assert diff.net_change == -1

    def test_empty(self):
        diff = compare_groups([], [])
        assert diff.total_changes == 0


class TestGroupDiff:
    def test_net_change(self):
        diff = GroupDiff(
            added=[_group(0, "a", 100, 2), _group(1, "b", 200, 3)],
            removed=[_group(2, "c", 300, 2)],
        )
        assert diff.net_change == 1


class TestFormatGroupDiff:
    def test_basic(self):
        diff = GroupDiff(
            added=[_group(0, "a", 100, 2)],
            removed=[_group(1, "b", 200, 3)],
            unchanged=5,
        )
        text = format_group_diff(diff)
        assert "Added:" in text
        assert "Removed:" in text
        assert "Unchanged:" in text
