"""Tests for DupeClean cleanup plan module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.plan import (
    CleanupPlan,
    PlanAction,
    create_cleanup_plan,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCreateCleanupPlan:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a/file.txt"), _fi("/b/file.txt")],
            )
        ]
        plan = create_cleanup_plan(groups)
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
        plan = create_cleanup_plan(groups)
        assert plan.total_actions == 3

    def test_empty_groups(self):
        plan = create_cleanup_plan([])
        assert plan.total_actions == 0


class TestCleanupPlan:
    def test_add(self):
        plan = CleanupPlan(name="test")
        plan.add(PlanAction(action_type="delete", source=Path("/a"), size=100))
        assert plan.total_actions == 1

    def test_total_savings(self):
        plan = CleanupPlan(name="test")
        plan.add(PlanAction(action_type="delete", source=Path("/a"), size=100))
        plan.add(PlanAction(action_type="delete", source=Path("/b"), size=200))
        assert plan.total_savings == 300

    def test_render_empty(self):
        plan = CleanupPlan(name="test")
        assert "test" in plan.render()

    def test_render_with_actions(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=500,
                files=[_fi("/a/data.bin"), _fi("/b/data.bin")],
            )
        ]
        plan = create_cleanup_plan(groups)
        text = plan.render()
        assert "delete" in text


class TestPlanAction:
    def test_size_display(self):
        action = PlanAction(action_type="delete", source=Path("/a"), size=1024)
        assert "B" in action.size_display
