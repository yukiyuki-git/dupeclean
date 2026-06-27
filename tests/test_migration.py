"""Tests for DupeClean file migration module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.migration import (
    MigrationAction,
    MigrationPlan,
    MigrationRule,
    create_migration_plan,
    execute_migration,
    format_migration_plan,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestCreateMigrationPlan:
    def test_basic(self):
        files = [
            _fi("/photos/IMG_001.jpg", 5000),
            _fi("/photos/IMG_002.jpg", 6000),
            _fi("/docs/report.pdf", 10000),
        ]
        rule = MigrationRule(
            name="archive_photos",
            source_pattern="*.jpg",
            destination=Path("/archive"),
        )
        plan = create_migration_plan(files, rule)
        assert plan.count == 2

    def test_size_filter(self):
        files = [
            _fi("/a/big.bin", 1000000),
            _fi("/b/small.bin", 100),
        ]
        rule = MigrationRule(
            name="large_files",
            source_pattern="*.bin",
            destination=Path("/archive"),
            min_size=1000,
        )
        plan = create_migration_plan(files, rule)
        assert plan.count == 1


class TestExecuteMigration:
    def test_dry_run(self, tmp_path):
        plan = MigrationPlan(
            actions=[
                MigrationAction(
                    source=tmp_path / "file.txt",
                    destination=tmp_path / "dest" / "file.txt",
                    reason="test",
                    size=100,
                ),
            ]
        )
        result = execute_migration(plan, dry_run=True)
        assert result["succeeded"] == 1


class TestMigrationPlan:
    def test_count(self):
        plan = MigrationPlan(
            actions=[
                MigrationAction(
                    source=Path("/a"),
                    destination=Path("/b"),
                    reason="test",
                    size=100,
                ),
            ]
        )
        assert plan.count == 1

    def test_total_size(self):
        plan = MigrationPlan(
            actions=[
                MigrationAction(
                    source=Path("/a"),
                    destination=Path("/b"),
                    reason="test",
                    size=100,
                ),
                MigrationAction(
                    source=Path("/c"),
                    destination=Path("/d"),
                    reason="test",
                    size=200,
                ),
            ]
        )
        assert plan.total_size == 300


class TestFormatMigrationPlan:
    def test_empty(self):
        plan = MigrationPlan()
        assert "No files" in format_migration_plan(plan)

    def test_with_actions(self):
        plan = MigrationPlan(
            actions=[
                MigrationAction(
                    source=Path("/test/file.txt"),
                    destination=Path("/archive/file.txt"),
                    reason="archive",
                    size=1000,
                ),
            ]
        )
        text = format_migration_plan(plan)
        assert "file.txt" in text
