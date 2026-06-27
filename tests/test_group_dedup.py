"""Tests for DupeClean group dedup module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_dedup import (
    GroupDedupResult,
    dedup_group_hardlink,
    dedup_groups_hardlink,
    format_dedup_result,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestDedupGroupHardlink:
    def test_dry_run(self, tmp_path):
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
        result = dedup_group_hardlink(group, dry_run=True)
        assert result.files_deduped == 1
        assert result.space_saved == 12

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
        result = dedup_group_hardlink(group, dry_run=False)
        assert result.files_deduped == 1
        assert a.exists()
        assert b.exists()


class TestDedupGroupsHardlink:
    def test_dry_run(self):
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
        result = dedup_groups_hardlink(groups, dry_run=True)
        assert result.groups_processed == 2
        assert result.files_deduped == 3


class TestGroupDedupResult:
    def test_saved_display(self):
        result = GroupDedupResult(space_saved=1024)
        assert "B" in result.saved_display


class TestFormatDedupResult:
    def test_basic(self):
        result = GroupDedupResult(groups_processed=5, files_deduped=10, space_saved=1000)
        text = format_dedup_result(result)
        assert "5" in text
        assert "10" in text
