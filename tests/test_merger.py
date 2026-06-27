"""Tests for DupeClean file merger module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.merger import (
    MergeAction,
    MergeResult,
    format_merge_result,
    merge_group,
    merge_groups,
    select_best_file,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestSelectBestFile:
    def test_shortest_path(self):
        files = [
            _fi("/very/long/nested/path/file.txt"),
            _fi("/short/file.txt"),
            _fi("/medium/path/file.txt"),
        ]
        assert select_best_file(files) == 1


class TestMergeGroup:
    def test_basic(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/a/file.txt"), _fi("/b/file.txt")],
        )
        action = merge_group(group)
        assert len(action.removed) == 1
        assert action.space_saved == 100


class TestMergeGroups:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="def",
                file_size=200,
                files=[_fi("/c"), _fi("/d"), _fi("/e")],
            ),
        ]
        result = merge_groups(groups)
        assert result.total_groups == 2
        assert result.total_files_removed == 3

    def test_empty_groups(self):
        result = merge_groups([])
        assert result.total_groups == 0


class TestMergeResult:
    def test_total_saved(self):
        result = MergeResult(
            actions=[
                MergeAction(group_id=0, keeper=_fi("/a"), space_saved=100),
                MergeAction(group_id=1, keeper=_fi("/c"), space_saved=200),
            ]
        )
        assert result.total_saved == 300


class TestFormatMergeResult:
    def test_basic(self):
        result = MergeResult(
            actions=[
                MergeAction(
                    group_id=0,
                    keeper=_fi("/a"),
                    removed=[_fi("/b")],
                    space_saved=100,
                ),
            ]
        )
        text = format_merge_result(result)
        assert "1 groups" in text
