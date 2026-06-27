"""Tests for DupeClean file deconfliction module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.deconflict import (
    ConflictResolution,
    format_conflict_report,
    resolve_batch_conflicts,
    resolve_conflict,
)


class TestResolveConflict:
    def test_no_conflict(self, tmp_path):
        target = tmp_path / "new.txt"
        resolution = resolve_conflict(target)
        assert resolution.was_conflict is False
        assert resolution.resolved == target

    def test_rename_strategy(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("content")
        resolution = resolve_conflict(target, "rename")
        assert resolution.was_conflict is True
        assert resolution.resolved != target
        assert "_1" in resolution.resolved.name

    def test_overwrite_strategy(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("content")
        resolution = resolve_conflict(target, "overwrite")
        assert resolution.was_conflict is True
        assert resolution.resolved == target

    def test_skip_strategy(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("content")
        resolution = resolve_conflict(target, "skip")
        assert resolution.was_conflict is True
        assert resolution.resolved == target

    def test_number_strategy(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("content")
        resolution = resolve_conflict(target, "number")
        assert resolution.was_conflict is True
        assert "_1" in resolution.resolved.name


class TestResolveBatchConflicts:
    def test_no_conflicts(self, tmp_path):
        targets = [
            tmp_path / "a.txt",
            tmp_path / "b.txt",
            tmp_path / "c.txt",
        ]
        results = resolve_batch_conflicts(targets)
        assert all(not r.was_conflict for r in results)

    def test_with_conflicts(self, tmp_path):
        (tmp_path / "file.txt").write_text("existing")
        targets = [
            tmp_path / "file.txt",
            tmp_path / "file.txt",
        ]
        results = resolve_batch_conflicts(targets)
        # Both should be resolved to different paths
        resolved = [r.resolved for r in results]
        assert len(set(resolved)) == len(resolved)


class TestFormatConflictReport:
    def test_no_conflicts(self):
        results = [
            ConflictResolution(
                original=Path("/a"),
                resolved=Path("/a"),
                strategy="rename",
                was_conflict=False,
            ),
        ]
        assert "No conflicts" in format_conflict_report(results)

    def test_with_conflicts(self, tmp_path):
        target = tmp_path / "existing.txt"
        target.write_text("x")
        resolution = resolve_conflict(target, "rename")
        text = format_conflict_report([resolution])
        assert "conflicts" in text.lower()
