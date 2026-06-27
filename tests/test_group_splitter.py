"""Tests for DupeClean group splitter module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_splitter import (
    SplitResult,
    format_split_result,
    split_by_max_count,
    split_by_size_range,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid, hash_value=f"h{gid}", file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestSplitByMaxCount:
    def test_no_split_needed(self):
        groups = [_group(0, 100, 5)]
        new_groups, result = split_by_max_count(groups, max_count=10)
        assert len(new_groups) == 1
        assert result.splits_performed == 0

    def test_split_needed(self):
        groups = [_group(0, 100, 25)]
        new_groups, result = split_by_max_count(groups, max_count=10)
        assert len(new_groups) == 3
        assert result.splits_performed == 1

    def test_single_file_not_split(self):
        groups = [
            DuplicateGroup(
                group_id=0, hash_value="abc", file_size=100,
                files=[_fi("/a")],
            )
        ]
        new_groups, _result = split_by_max_count(groups, max_count=10)
        # Single-file groups pass through unchanged
        assert len(new_groups) == 1


class TestSplitBySizeRange:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 1000000, 2)]
        large, small = split_by_size_range(groups, max_size=500)
        assert len(large) == 1
        assert len(small) == 1


class TestSplitResult:
    def test_expansion(self):
        result = SplitResult(original_groups=5, split_groups=8)
        assert result.expansion == 3


class TestFormatSplitResult:
    def test_basic(self):
        result = SplitResult(
            original_groups=5, split_groups=8, splits_performed=3
        )
        text = format_split_result(result)
        assert "5" in text
        assert "8" in text
