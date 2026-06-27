"""Tests for DupeClean group formatter v2 module."""

from __future__ import annotations

import json
from pathlib import Path

from dupeclean.group_formatter_v2 import (
    format_group_json,
    format_group_summary_brief,
    format_group_table,
    format_group_tree,
    format_groups_json,
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


class TestFormatGroupJson:
    def test_basic(self):
        group = _group(0, 1000, 3)
        data = format_group_json(group)
        assert data["group_id"] == 0
        assert data["count"] == 3
        assert len(data["files"]) == 3


class TestFormatGroupsJson:
    def test_valid_json(self):
        groups = [_group(0, 100, 2), _group(1, 200, 3)]
        text = format_groups_json(groups)
        data = json.loads(text)
        assert len(data) == 2


class TestFormatGroupTable:
    def test_empty(self):
        assert "No groups" in format_group_table([])

    def test_basic(self):
        groups = [_group(0, 100, 2)]
        text = format_group_table(groups)
        assert "Files" in text or "Size" in text


class TestFormatGroupTree:
    def test_basic(self):
        group = _group(0, 100, 3)
        text = format_group_tree(group)
        assert "Group #0" in text
        assert "KEEP" in text
        assert "DUP" in text


class TestFormatGroupSummaryBrief:
    def test_basic(self):
        group = _group(0, 1000, 3)
        text = format_group_summary_brief(group)
        assert "Group #0" in text
        assert "3 x" in text
