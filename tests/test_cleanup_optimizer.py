"""Tests for DupeClean cleanup optimizer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.cleanup_optimizer import (
    OptimizedPlan,
    format_optimized_plan,
    optimize_cleanup,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestOptimizeCleanup:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=10000,
                files=[_fi("/a"), _fi("/b"), _fi("/c")],
            )
        ]
        plan = optimize_cleanup(groups)
        assert plan.optimized_actions == 2
        assert plan.estimated_savings == 20000

    def test_skips_tiny_files(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a", 100), _fi("/b", 100)],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="def",
                file_size=10000,
                files=[_fi("/c", 10000), _fi("/d", 10000)],
            ),
        ]
        plan = optimize_cleanup(groups)
        assert plan.optimized_actions == 1  # Only the large group
        assert len(plan.optimizations) == 1

    def test_empty_groups(self):
        plan = optimize_cleanup([])
        assert plan.optimized_actions == 0


class TestOptimizedPlan:
    def test_savings_display(self):
        plan = OptimizedPlan(estimated_savings=1024)
        assert "B" in plan.savings_display


class TestFormatOptimizedPlan:
    def test_basic(self):
        plan = OptimizedPlan(
            original_groups=5,
            optimized_actions=3,
            estimated_savings=1000,
        )
        text = format_optimized_plan(plan)
        assert "5" in text
        assert "3" in text
