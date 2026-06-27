"""Tests for DupeClean group conflict resolver."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_conflict import (
    Conflict,
    ConflictResolver,
    format_conflicts,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestConflictResolver:
    def test_detect_size_mismatch(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"x" * 100)
        b.write_bytes(b"y" * 200)
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        resolver = ConflictResolver()
        conflicts = resolver.detect(groups)
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "size_mismatch"

    def test_detect_no_conflicts(self, tmp_path):
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
        resolver = ConflictResolver()
        conflicts = resolver.detect(groups)
        assert len(conflicts) == 0

    def test_auto_resolve(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"x" * 100)
        b.write_bytes(b"y" * 200)
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[FileInfo.from_path(a), FileInfo.from_path(b)],
            )
        ]
        resolver = ConflictResolver()
        resolver.detect(groups)
        resolutions = resolver.auto_resolve()
        assert len(resolutions) == 1
        assert resolutions[0].resolution_type == "skip"

    def test_has_conflicts(self):
        resolver = ConflictResolver()
        assert resolver.has_conflicts is False
        resolver.conflicts.append(Conflict(group_id=0, conflict_type="test", description="test"))
        assert resolver.has_conflicts is True


class TestFormatConflicts:
    def test_no_conflicts(self):
        resolver = ConflictResolver()
        assert "No conflicts" in format_conflicts(resolver)

    def test_with_conflicts(self):
        resolver = ConflictResolver()
        resolver.conflicts.append(
            Conflict(group_id=0, conflict_type="test", description="Test conflict")
        )
        text = format_conflicts(resolver)
        assert "1" in text
