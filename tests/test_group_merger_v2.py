"""Tests for DupeClean group merger v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_merger_v2 import (
    MergeConflict,
    MergeResultV2,
    format_merge_result_v2,
    merge_groups_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestMergeGroupsV2:
    def test_no_overlap(self):
        groups = [
            DuplicateGroup(group_id=0, hash_value="a", file_size=100,
                           files=[_fi("/a"), _fi("/b")]),
            DuplicateGroup(group_id=1, hash_value="b", file_size=200,
                           files=[_fi("/c"), _fi("/d")]),
        ]
        merged, result = merge_groups_v2(groups)
        assert len(merged) == 2
        assert result.groups_merged == 0

    def test_with_overlap(self):
        shared = _fi("/shared")
        groups = [
            DuplicateGroup(group_id=0, hash_value="a", file_size=100,
                           files=[_fi("/a"), shared]),
            DuplicateGroup(group_id=1, hash_value="b", file_size=100,
                           files=[shared, _fi("/c")]),
        ]
        merged, result = merge_groups_v2(groups)
        assert len(merged) == 1
        assert result.groups_merged == 1

    def test_empty(self):
        merged, _result = merge_groups_v2([])
        assert len(merged) == 0


class TestMergeResultV2:
    def test_reduction(self):
        result = MergeResultV2(original_count=10, merged_count=7)
        assert result.reduction == 3

    def test_has_conflicts(self):
        result = MergeResultV2(conflicts=[MergeConflict(group_a_id=0, group_b_id=1)])
        assert result.has_conflicts is True


class TestFormatMergeResultV2:
    def test_basic(self):
        result = MergeResultV2(original_count=10, merged_count=7, groups_merged=3)
        text = format_merge_result_v2(result)
        assert "10" in text
        assert "7" in text
