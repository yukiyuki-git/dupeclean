"""Tests for DupeClean consolidation module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.consolidate import (
    create_plan,
    execute_consolidation,
    format_plan,
    hardlink_duplicates,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=[_fi("/a.txt", 1000), _fi("/b.txt", 1000)],
        ),
        DuplicateGroup(
            group_id=1,
            hash_value="def",
            file_size=2000,
            files=[
                _fi("/c.bin", 2000),
                _fi("/d.bin", 2000),
                _fi("/e.bin", 2000),
            ],
        ),
    ]


class TestCreatePlan:
    def test_basic_plan(self):
        groups = _make_groups()
        plan = create_plan(groups)
        assert plan.total_duplicates == 3  # 1 + 2
        assert plan.total_wasted == 5000  # 1000 + 4000

    def test_custom_strategy(self):
        groups = _make_groups()
        plan = create_plan(groups, strategy="newest")
        assert plan.keep_strategy == "newest"

    def test_summary(self):
        groups = _make_groups()
        plan = create_plan(groups)
        assert "groups" in plan.summary


class TestExecuteConsolidation:
    def test_dry_run(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")

        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=4,
                files=[
                    FileInfo.from_path(a),
                    FileInfo.from_path(b),
                ],
            )
        ]
        plan = create_plan(groups)
        results = execute_consolidation(plan, dry_run=True)
        assert len(results) == 1
        assert results[0].files_processed >= 0


class TestHardlinkDuplicates:
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
                files=[
                    FileInfo.from_path(a),
                    FileInfo.from_path(b),
                ],
            )
        ]
        count = hardlink_duplicates(groups, dry_run=False)
        assert count == 1
        assert a.exists()
        assert b.exists()

    def test_dry_run(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")

        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=4,
                files=[
                    FileInfo.from_path(a),
                    FileInfo.from_path(b),
                ],
            )
        ]
        count = hardlink_duplicates(groups, dry_run=True)
        assert count == 1


class TestFormatPlan:
    def test_contains_strategy(self):
        groups = _make_groups()
        plan = create_plan(groups)
        text = format_plan(plan)
        assert "shortest_path" in text

    def test_shows_groups(self):
        groups = _make_groups()
        plan = create_plan(groups)
        text = format_plan(plan)
        assert "Group #0" in text
        assert "Group #1" in text

    def test_shows_keep_link(self):
        groups = _make_groups()
        plan = create_plan(groups)
        text = format_plan(plan)
        assert "KEEP:" in text
        assert "LINK:" in text
