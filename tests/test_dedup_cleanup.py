"""Tests for DupeClean dedup cleanup module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_cleanup import (
    CleanupStats,
    cleanup_duplicates,
    format_cleanup_stats,
)
from dupeclean.models import CleanupAction, DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupDuplicates:
    def test_dry_run_delete(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")

        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=4,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        stats = cleanup_duplicates(groups, CleanupAction.DELETE, dry_run=True)
        assert stats.files_processed == 1
        assert a.exists()
        assert b.exists()

    def test_actual_delete(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")

        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=4,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        stats = cleanup_duplicates(groups, CleanupAction.DELETE, dry_run=False)
        assert stats.files_deleted == 1
        assert a.exists()
        assert not b.exists()

    def test_hardlink(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same content")
        b.write_bytes(b"same content")

        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=12,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        stats = cleanup_duplicates(groups, CleanupAction.HARDLINK, dry_run=False)
        assert stats.hardlinks_created == 1
        assert a.exists()
        assert b.exists()


class TestCleanupStats:
    def test_success_count(self):
        stats = CleanupStats(files_deleted=5, hardlinks_created=3)
        assert stats.success_count == 8

    def test_freed_display(self):
        stats = CleanupStats(space_freed=1024)
        assert "B" in stats.freed_display


class TestFormatCleanupStats:
    def test_basic(self):
        stats = CleanupStats(
            files_processed=10,
            files_deleted=8,
            space_freed=5000,
        )
        text = format_cleanup_stats(stats)
        assert "10" in text
        assert "8" in text

    def test_with_errors(self):
        stats = CleanupStats(errors=["Permission denied: /test/file.txt"])
        text = format_cleanup_stats(stats)
        assert "Error" in text
