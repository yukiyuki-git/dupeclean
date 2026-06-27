"""Tests for DupeClean group merger module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_merger import (
    MergeResult,
    format_merge_result,
    merge_overlapping_groups,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestMergeOverlappingGroups:
    def test_no_overlap(self):
        groups = [
            DuplicateGroup(group_id=0, hash_value="a", file_size=100,
                           files=[_fi("/a"), _fi("/b")]),
            DuplicateGroup(group_id=1, hash_value="b", file_size=200,
                           files=[_fi("/c"), _fi("/d")]),
        ]
        merged, result = merge_overlapping_groups(groups)
        assert len(merged) == 2
        assert result.groups_merged == 0

    def test_with_overlap(self):
        shared = _fi("/shared", 100)
        groups = [
            DuplicateGroup(group_id=0, hash_value="a", file_size=100,
                           files=[_fi("/a"), shared]),
            DuplicateGroup(group_id=1, hash_value="b", file_size=100,
                           files=[shared, _fi("/c")]),
        ]
        merged, result = merge_overlapping_groups(groups)
        assert len(merged) == 1
        assert result.groups_merged == 1

    def test_empty(self):
        merged, _result = merge_overlapping_groups([])
        assert len(merged) == 0


class TestMergeResult:
    def test_reduction(self):
        result = MergeResult(original_count=10, merged_count=7)
        assert result.reduction == 3
        assert result.reduction_pct == 30.0

    def test_zero_original(self):
        result = MergeResult()
        assert result.reduction_pct == 0.0


class TestFormatMergeResult:
    def test_basic(self):
        result = MergeResult(original_count=10, merged_count=7, groups_merged=3)
        text = format_merge_result(result)
        assert "10" in text
        assert "7" in text
