"""Tests for DupeClean dedup diff module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_diff import (
    DedupDiff,
    diff_dedup_results,
    format_dedup_diff,
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


class TestDiffDedupResults:
    def test_no_changes(self):
        old = [_group(0, "abc", 100, 2)]
        new = [_group(0, "abc", 100, 2)]
        diff = diff_dedup_results(old, new)
        assert diff.unchanged_groups == 1
        assert diff.total_changes == 0

    def test_added_groups(self):
        old = [_group(0, "abc", 100, 2)]
        new = [
            _group(0, "abc", 100, 2),
            _group(1, "def", 200, 3),
        ]
        diff = diff_dedup_results(old, new)
        assert len(diff.added_groups) == 1
        assert diff.net_change == 1

    def test_removed_groups(self):
        old = [
            _group(0, "abc", 100, 2),
            _group(1, "def", 200, 3),
        ]
        new = [_group(0, "abc", 100, 2)]
        diff = diff_dedup_results(old, new)
        assert len(diff.removed_groups) == 1
        assert diff.net_change == -1

    def test_mixed_changes(self):
        old = [
            _group(0, "abc", 100, 2),
            _group(1, "def", 200, 3),
        ]
        new = [
            _group(0, "abc", 100, 2),
            _group(2, "ghi", 300, 4),
        ]
        diff = diff_dedup_results(old, new)
        assert diff.unchanged_groups == 1
        assert len(diff.added_groups) == 1
        assert len(diff.removed_groups) == 1

    def test_empty(self):
        diff = diff_dedup_results([], [])
        assert diff.total_changes == 0


class TestDedupDiff:
    def test_net_change(self):
        diff = DedupDiff(old_groups=5, new_groups=8)
        assert diff.net_change == 3


class TestFormatDedupDiff:
    def test_basic(self):
        diff = DedupDiff(
            old_groups=5,
            new_groups=8,
            unchanged_groups=3,
            added_groups=[_group(0, "a", 100, 2)],
            removed_groups=[_group(1, "b", 200, 3)],
        )
        text = format_dedup_diff(diff)
        assert "Old groups" in text
        assert "New groups" in text
        assert "+3" in text

    def test_no_changes(self):
        diff = DedupDiff(old_groups=5, new_groups=5)
        text = format_dedup_diff(diff)
        assert "+0" in text
