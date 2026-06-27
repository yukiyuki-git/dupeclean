"""Tests for DupeClean group cleanup v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_cleanup_v2 import (
    CleanupActionV2,
    CleanupResultV2,
    cleanup_group_v2,
    format_cleanup_result_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupGroupV2:
    def test_dry_run(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=4,
            files=[FileInfo.from_path(a), FileInfo.from_path(b)],
        )
        result = cleanup_group_v2(group, dry_run=True)
        assert result.succeeded == 1
        assert result.verified == 1

    def test_actual_delete(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=4,
            files=[FileInfo.from_path(a), FileInfo.from_path(b)],
        )
        result = cleanup_group_v2(group, action="delete", dry_run=False)
        assert result.succeeded == 1
        assert a.exists()
        assert not b.exists()

    def test_actual_hardlink(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same content")
        b.write_bytes(b"same content")
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=12,
            files=[FileInfo.from_path(a), FileInfo.from_path(b)],
        )
        result = cleanup_group_v2(group, action="hardlink", dry_run=False)
        assert result.succeeded == 1
        assert result.verified == 1


class TestCleanupResultV2:
    def test_total_freed(self):
        result = CleanupResultV2(
            actions=[
                CleanupActionV2(source=Path("/a"), action_type="delete", size=100, success=True),
                CleanupActionV2(source=Path("/b"), action_type="delete", size=200, success=True),
            ]
        )
        assert result.total_freed == 300


class TestFormatCleanupResultV2:
    def test_basic(self):
        result = CleanupResultV2(
            actions=[
                CleanupActionV2(source=Path("/a"), action_type="delete", size=100, success=True),
            ]
        )
        text = format_cleanup_result_v2(result)
        assert "1/1" in text
