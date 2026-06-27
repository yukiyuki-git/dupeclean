"""Tests for DupeClean deduplication engine."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_engine import (
    DedupPlan,
    DedupResult,
    create_dedup_plan,
    execute_dedup,
    format_dedup_plan,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCreateDedupPlan:
    def test_basic_plan(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a.txt", 1000), _fi("/b.txt", 1000)],
            ),
        ]
        plan = create_dedup_plan(groups)
        assert plan.count == 1
        assert plan.total_space_saved == 1000

    def test_multiple_groups(self):
        groups = [
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
        plan = create_dedup_plan(groups)
        assert plan.count == 3  # 1 + 2
        assert plan.total_space_saved == 5000  # 1000 + 4000

    def test_single_file_group_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a.txt", 1000)],
            ),
        ]
        plan = create_dedup_plan(groups)
        assert plan.count == 0

    def test_method_parameter(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a.txt", 1000), _fi("/b.txt", 1000)],
            ),
        ]
        plan = create_dedup_plan(groups, method="symlink")
        assert plan.actions[0].method == "symlink"


class TestExecuteDedup:
    def test_dry_run(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a.txt", 1000), _fi("/b.txt", 1000)],
            ),
        ]
        plan = create_dedup_plan(groups)
        result = execute_dedup(plan, dry_run=True)
        assert result.actions_completed == 1
        assert result.space_saved == 1000

    def test_actual_hardlink(self, tmp_path):
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
            ),
        ]
        plan = create_dedup_plan(groups)
        result = execute_dedup(plan, dry_run=False, verify=False)
        assert result.actions_completed == 1
        assert a.exists()
        assert b.exists()


class TestDedupPlan:
    def test_savings_display(self):
        plan = DedupPlan(total_space_saved=1024)
        assert "B" in plan.savings_display


class TestDedupResult:
    def test_defaults(self):
        result = DedupResult()
        assert result.actions_completed == 0
        assert result.actions_failed == 0
        assert result.space_saved == 0


class TestFormatDedupPlan:
    def test_contains_info(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a.txt", 1000), _fi("/b.txt", 1000)],
            ),
        ]
        plan = create_dedup_plan(groups)
        text = format_dedup_plan(plan)
        assert "hardlink" in text
        assert "savings" in text
