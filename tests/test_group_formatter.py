"""Tests for DupeClean group formatter module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_formatter import (
    format_group_detail,
    format_group_list,
    format_group_tree,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"hash_{gid}" * 4,
        file_size=size,
        files=[_fi(f"/path/to/file_{i}.txt", size) for i in range(count)],
    )


class TestFormatGroupDetail:
    def test_basic(self):
        group = _group(0, 1000, 3)
        text = format_group_detail(group)
        assert "Group #0" in text
        assert "3" in text
        assert "KEEP" in text
        assert "DUP" in text

    def test_single_file(self):
        group = _group(0, 100, 1)
        text = format_group_detail(group)
        assert "Group #0" in text


class TestFormatGroupList:
    def test_empty(self):
        assert "No duplicate" in format_group_list([])

    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 200, 3)]
        text = format_group_list(groups)
        assert "2" in text
        assert "Group" in text or "#" in text

    def test_many_groups(self):
        groups = [_group(i, 100, 2) for i in range(50)]
        text = format_group_list(groups)
        assert "more" in text


class TestFormatGroupTree:
    def test_basic(self):
        group = _group(0, 100, 3)
        text = format_group_tree(group)
        assert "Group #0" in text
        assert "KEEP" in text
        assert "DUP" in text

    def test_indented(self):
        group = _group(0, 100, 2)
        text = format_group_tree(group, indent=4)
        assert "    ├" in text
