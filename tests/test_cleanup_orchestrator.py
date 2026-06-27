"""Tests for DupeClean cleanup orchestrator."""

from __future__ import annotations

from pathlib import Path

from dupeclean.cleanup_orchestrator import (
    CleanupOrchestrator,
    CleanupStep,
    create_standard_orchestrator,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupOrchestrator:
    def test_add_step(self):
        orch = CleanupOrchestrator()
        orch.add_step("validate")
        assert len(orch.steps) == 1

    def test_progress_empty(self):
        orch = CleanupOrchestrator()
        assert orch.progress == 0.0

    def test_progress_partial(self):
        orch = CleanupOrchestrator()
        orch.add_step("a")
        orch.add_step("b")
        orch.steps[0].status = "completed"
        assert orch.progress == 0.5

    def test_is_complete(self):
        orch = CleanupOrchestrator()
        orch.add_step("a")
        orch.steps[0].status = "completed"
        assert orch.is_complete is True

    def test_has_failures(self):
        orch = CleanupOrchestrator()
        orch.add_step("a")
        orch.steps[0].status = "failed"
        assert orch.has_failures is True

    def test_render(self):
        orch = CleanupOrchestrator()
        orch.add_step("validate")
        orch.add_step("execute")
        text = orch.render()
        assert "validate" in text
        assert "execute" in text


class TestCreateStandardOrchestrator:
    def test_has_steps(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        orch = create_standard_orchestrator(groups)
        assert len(orch.steps) == 6
        assert orch.groups == groups


class TestCleanupStep:
    def test_default_status(self):
        step = CleanupStep(name="test")
        assert step.status == "pending"
