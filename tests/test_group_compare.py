"""Tests for DupeClean group comparison module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_compare import (
    GroupComparison,
    compare_group_sets,
    format_comparison,
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


class TestCompareGroupSets:
    def test_no_changes(self):
        old = [_group(0, "abc", 100, 2)]
        new = [_group(0, "abc", 100, 2)]
        comp = compare_group_sets(old, new)
        assert comp.unchanged == 1
        assert comp.total_changes == 0

    def test_added_groups(self):
        old = [_group(0, "abc", 100, 2)]
        new = [_group(0, "abc", 100, 2), _group(1, "def", 200, 3)]
        comp = compare_group_sets(old, new)
        assert len(comp.added) == 1
        assert comp.net_change == 1

    def test_removed_groups(self):
        old = [_group(0, "abc", 100, 2), _group(1, "def", 200, 3)]
        new = [_group(0, "abc", 100, 2)]
        comp = compare_group_sets(old, new)
        assert len(comp.removed) == 1
        assert comp.net_change == -1

    def test_empty(self):
        comp = compare_group_sets([], [])
        assert comp.total_changes == 0


class TestGroupComparison:
    def test_net_change(self):
        comp = GroupComparison(
            added=[_group(0, "a", 100, 2), _group(1, "b", 200, 3)],
            removed=[_group(2, "c", 300, 2)],
        )
        assert comp.net_change == 1


class TestFormatComparison:
    def test_basic(self):
        comp = GroupComparison(
            added=[_group(0, "a", 100, 2)],
            removed=[_group(1, "b", 200, 3)],
            unchanged=5,
        )
        text = format_comparison(comp)
        assert "Added:" in text
        assert "Removed:" in text
        assert "Unchanged:" in text
