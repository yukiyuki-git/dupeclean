"""Tests for DupeClean cleanup plan v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.plan_v2 import (
    CleanupPlanV2,
    PlanActionV2,
    create_plan_v2,
    format_plan_v2,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCreatePlanV2:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a/file.txt"), _fi("/b/file.txt")],
            )
        ]
        plan = create_plan_v2(groups)
        assert plan.total_actions == 1
        assert plan.total_savings == 100

    def test_multiple_groups(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="a",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="b",
                file_size=200,
                files=[_fi("/c"), _fi("/d"), _fi("/e")],
            ),
        ]
        plan = create_plan_v2(groups)
        assert plan.total_actions == 3

    def test_empty_groups(self):
        plan = create_plan_v2([])
        assert plan.total_actions == 0


class TestCleanupPlanV2:
    def test_add(self):
        plan = CleanupPlanV2(name="test")
        plan.add(PlanActionV2(action_type="delete", source=Path("/a"), size=100))
        assert plan.total_actions == 1

    def test_render(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=500,
                files=[_fi("/a/data.bin"), _fi("/b/data.bin")],
            )
        ]
        plan = create_plan_v2(groups)
        text = format_plan_v2(plan)
        assert "delete" in text


class TestPlanActionV2:
    def test_size_display(self):
        action = PlanActionV2(action_type="delete", source=Path("/a"), size=1024)
        assert "B" in action.size_display
