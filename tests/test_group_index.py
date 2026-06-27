"""Tests for DupeClean group indexer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_index import (
    GroupIndex,
    build_group_index,
    format_group_index,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, ext: str = ".txt") -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}{ext}", size) for i in range(2)],
    )


class TestGroupIndex:
    def test_add_group(self):
        index = GroupIndex()
        index.add_group(_group(0, 100))
        assert index.total_files == 2

    def test_get_group_for_file(self):
        index = GroupIndex()
        index.add_group(_group(0, 100))
        assert index.get_group_for_file(Path("/f0.txt")) == 0
        assert index.get_group_for_file(Path("/nope")) is None

    def test_get_groups_by_ext(self):
        index = GroupIndex()
        index.add_group(_group(0, 100))
        index.add_group(_group(1, 200))
        # Both groups use .txt, 2 files each = 4 entries
        assert len(index.get_groups_by_ext(".txt")) == 4

    def test_get_groups_by_size(self):
        index = GroupIndex()
        index.add_group(_group(0, 100))
        index.add_group(_group(1, 100))
        assert len(index.get_groups_by_size(100)) == 2


class TestBuildGroupIndex:
    def test_basic(self):
        groups = [_group(0, 100), _group(1, 200)]
        index = build_group_index(groups)
        # Both groups use same file paths, so last group wins in by_path
        assert index.total_files == 2
        assert index.total_groups == 2


class TestFormatGroupIndex:
    def test_basic(self):
        index = build_group_index([_group(0, 100)])
        text = format_group_index(index)
        assert "2" in text
