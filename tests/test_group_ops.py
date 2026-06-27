"""Tests for DupeClean group operations module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_ops import (
    count_total_files,
    count_total_waste,
    flatten_groups,
    format_group_summary,
    get_file_sizes,
    get_group_sizes,
    get_unique_extensions,
    merge_groups,
    split_by_count,
    split_by_size,
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


class TestMergeGroups:
    def test_basic(self):
        g1 = [_group(0, 100, 2)]
        g2 = [_group(1, 200, 3)]
        merged = merge_groups([g1, g2])
        assert len(merged) == 2


class TestFlattenGroups:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 200, 3)]
        files = flatten_groups(groups)
        assert len(files) == 5


class TestCountTotalFiles:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 200, 3)]
        assert count_total_files(groups) == 5


class TestCountTotalWaste:
    def test_basic(self):
        groups = [_group(0, 100, 3), _group(1, 100, 2)]
        assert count_total_waste(groups) == 300  # 200 + 100


class TestGetUniqueExtensions:
    def test_basic(self):
        groups = [_group(0, 100, 2, ".txt"), _group(1, 100, 2, ".py")]
        exts = get_unique_extensions(groups)
        assert ".txt" in exts
        assert ".py" in exts


class TestGetGroupSizes:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        sizes = get_group_sizes(groups)
        assert sizes == [2, 5]


class TestGetFileSizes:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 200, 2)]
        sizes = get_file_sizes(groups)
        assert sizes == [100, 200]


class TestSplitBySize:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 1000, 2)]
        large, small = split_by_size(groups, 500)
        assert len(large) == 1
        assert len(small) == 1


class TestSplitByCount:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 100, 10)]
        many, few = split_by_count(groups, 5)
        assert len(many) == 1
        assert len(few) == 1


class TestFormatGroupSummary:
    def test_empty(self):
        assert "No duplicate" in format_group_summary([])

    def test_basic(self):
        groups = [_group(0, 100, 2, ".txt")]
        text = format_group_summary(groups)
        assert "1" in text
