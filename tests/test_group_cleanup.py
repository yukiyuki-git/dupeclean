"""Tests for DupeClean group cleanup module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_cleanup import (
    BatchCleanupResult,
    GroupCleanupResult,
    batch_cleanup,
    cleanup_group_delete,
    cleanup_group_hardlink,
    format_batch_cleanup,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupGroupDelete:
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
        result = cleanup_group_delete(group, dry_run=True)
        assert result.files_removed == 1
        assert result.space_freed == 4
        assert a.exists()  # Not deleted in dry run

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
        result = cleanup_group_delete(group, dry_run=False)
        assert result.files_removed == 1
        assert a.exists()
        assert not b.exists()


class TestCleanupGroupHardlink:
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
        result = cleanup_group_hardlink(group, dry_run=True)
        assert result.hardlinks_created == 1


class TestBatchCleanup:
    def test_dry_run(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        result = batch_cleanup(groups, action="delete", dry_run=True)
        assert result.total_groups == 1
        assert result.total_removed == 1


class TestGroupCleanupResult:
    def test_freed_display(self):
        result = GroupCleanupResult(group_id=0, space_freed=1024)
        assert "B" in result.freed_display


class TestFormatBatchCleanup:
    def test_basic(self):
        result = BatchCleanupResult()
        result.results.append(GroupCleanupResult(group_id=0, files_removed=1, space_freed=100))
        text = format_batch_cleanup(result)
        assert "1 groups" in text
