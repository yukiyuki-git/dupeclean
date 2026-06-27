"""Tests for DupeClean deduplicator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.deduplicator import (
    DedupAction,
    DedupResult,
    deduplicate_group,
    deduplicate_groups,
    format_dedup_result,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestDeduplicateGroup:
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
        result = deduplicate_group(group, dry_run=True)
        assert result.succeeded == 1

    def test_actual_dedup(self, tmp_path):
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
        result = deduplicate_group(group, dry_run=False)
        assert result.succeeded == 1
        assert a.exists()
        assert b.exists()

    def test_single_file_skipped(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/a")],
        )
        result = deduplicate_group(group)
        assert result.total == 0


class TestDeduplicateGroups:
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
        result = deduplicate_groups(groups, dry_run=True)
        assert result.total == 3  # 1 + 2


class TestDedupResult:
    def test_space_saved(self):
        result = DedupResult(
            actions=[
                DedupAction(source=Path("/a"), target=Path("/b"), size=100, success=True),
                DedupAction(source=Path("/c"), target=Path("/d"), size=200, success=True),
            ]
        )
        assert result.space_saved == 300


class TestFormatDedupResult:
    def test_basic(self):
        result = DedupResult(
            actions=[
                DedupAction(source=Path("/a"), target=Path("/b"), size=100, success=True),
            ]
        )
        text = format_dedup_result(result)
        assert "1" in text
