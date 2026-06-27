"""Tests for DupeClean cleanup workflow module."""

from __future__ import annotations

from dupeclean.cleanup_workflow import (
    CleanupWorkflow,
    WorkflowStep,
    create_cleanup_workflow,
)


class TestCleanupWorkflow:
    def test_add_step(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("step1")
        assert len(wf.steps) == 1

    def test_progress_empty(self):
        wf = CleanupWorkflow(name="test")
        assert wf.progress == 0.0

    def test_progress_partial(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.add_step("b")
        wf.steps[0].status = "completed"
        assert wf.progress == 0.5

    def test_is_complete(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.steps[0].status = "completed"
        assert wf.is_complete is True

    def test_current(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.add_step("b")
        assert wf.current is not None
        assert wf.current.name == "a"

    def test_advance(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.add_step("b")
        wf.advance()
        assert wf.current_step == 1

    def test_complete_current(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.add_step("b")
        wf.complete_current()
        assert wf.steps[0].status == "completed"
        assert wf.current_step == 1

    def test_fail_current(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("a")
        wf.fail_current("error message")
        assert wf.steps[0].status == "failed"

    def test_render(self):
        wf = CleanupWorkflow(name="test")
        wf.add_step("scan")
        wf.add_step("execute")
        text = wf.render()
        assert "test" in text
        assert "scan" in text


class TestCreateCleanupWorkflow:
    def test_has_steps(self):
        wf = create_cleanup_workflow()
        assert len(wf.steps) == 7
        assert wf.name == "Standard Cleanup"


class TestWorkflowStep:
    def test_default_status(self):
        step = WorkflowStep(name="test")
        assert step.status == "pending"
