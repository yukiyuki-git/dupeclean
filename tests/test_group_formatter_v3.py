"""Tests for DupeClean group formatter v3 module."""

from __future__ import annotations

import json
from pathlib import Path

from dupeclean.group_formatter_v3 import (
    format_group_rich,
    format_groups_compact,
    format_groups_json_compact,
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


class TestFormatGroupRich:
    def test_basic(self):
        group = _group(0, 1000, 3)
        text = format_group_rich(group)
        assert "Group #0" in text
        assert "★" in text
        assert "✗" in text

    def test_with_bar(self):
        group = _group(0, 100, 5)
        text = format_group_rich(group)
        assert "█" in text or "░" in text


class TestFormatGroupsCompact:
    def test_empty(self):
        assert "No duplicate" in format_groups_compact([])

    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 200, 3)]
        text = format_groups_compact(groups)
        assert "Files" in text
        assert "Wasted" in text

    def test_many_groups(self):
        groups = [_group(i, 100, 2) for i in range(50)]
        text = format_groups_compact(groups)
        assert "more" in text


class TestFormatGroupsJsonCompact:
    def test_valid_json(self):
        groups = [_group(0, 100, 2)]
        text = format_groups_json_compact(groups)
        data = json.loads(text)
        assert len(data) == 1
        assert data[0]["id"] == 0
