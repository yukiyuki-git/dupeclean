"""Tests for DupeClean group sort module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_sort import (
    SORT_FUNCTIONS,
    format_sort_info,
    sort_by_count,
    sort_by_group_id,
    sort_by_size,
    sort_by_waste,
    sort_groups,
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


class TestSortByWaste:
    def test_descending(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        sorted_g = sort_by_waste(groups)
        assert sorted_g[0].count == 5

    def test_ascending(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        sorted_g = sort_by_waste(groups, reverse=False)
        assert sorted_g[0].count == 2


class TestSortByCount:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        sorted_g = sort_by_count(groups)
        assert sorted_g[0].count == 5


class TestSortBySize:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 1000, 2)]
        sorted_g = sort_by_size(groups)
        assert sorted_g[0].file_size == 1000


class TestSortByGroupId:
    def test_basic(self):
        groups = [_group(2, 100, 2), _group(0, 100, 2), _group(1, 100, 2)]
        sorted_g = sort_by_group_id(groups)
        assert sorted_g[0].group_id == 0


class TestSortGroups:
    def test_by_waste(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        sorted_g = sort_groups(groups, "waste")
        assert sorted_g[0].count == 5

    def test_unknown_sort(self):
        groups = [_group(0, 100, 2)]
        sorted_g = sort_groups(groups, "unknown")
        assert len(sorted_g) == 1


class TestSortFunctions:
    def test_all_exist(self):
        expected = {"waste", "count", "size", "id"}
        assert set(SORT_FUNCTIONS.keys()) == expected


class TestFormatSortInfo:
    def test_basic(self):
        groups = [_group(0, 100, 2)]
        text = format_sort_info(groups, "waste")
        assert "1 groups" in text

    def test_empty(self):
        assert "No groups" in format_sort_info([], "waste")
