"""Tests for DupeClean workflow module."""

from __future__ import annotations

from dupeclean.workflow import (
    Workflow,
    WorkflowStep,
    create_cleanup_workflow,
    create_quick_workflow,
    create_standard_workflow,
    format_workflow,
)


class TestWorkflow:
    def test_add_step(self):
        wf = Workflow(name="test")
        wf.add_step("scan", "Scan files")
        assert len(wf.steps) == 1

    def test_progress_empty(self):
        wf = Workflow(name="test")
        assert wf.progress == 0.0

    def test_progress_partial(self):
        wf = Workflow(name="test")
        wf.add_step("a", "do a")
        wf.add_step("b", "do b")
        wf.steps[0].status = "completed"
        assert wf.progress == 0.5

    def test_is_complete(self):
        wf = Workflow(name="test")
        wf.add_step("a", "do a")
        wf.steps[0].status = "completed"
        assert wf.is_complete is True

    def test_is_not_complete(self):
        wf = Workflow(name="test")
        wf.add_step("a", "do a")
        assert wf.is_complete is False

    def test_has_failures(self):
        wf = Workflow(name="test")
        wf.add_step("a", "do a")
        wf.steps[0].status = "failed"
        assert wf.has_failures is True

    def test_no_failures(self):
        wf = Workflow(name="test")
        wf.add_step("a", "do a")
        wf.steps[0].status = "completed"
        assert wf.has_failures is False


class TestWorkflowStep:
    def test_default_status(self):
        step = WorkflowStep(name="test", action="do")
        assert step.status == "pending"


class TestCreateStandardWorkflow:
    def test_has_steps(self):
        wf = create_standard_workflow()
        assert len(wf.steps) == 5
        assert wf.name == "Standard Dedup"


class TestCreateQuickWorkflow:
    def test_has_steps(self):
        wf = create_quick_workflow()
        assert len(wf.steps) == 3


class TestCreateCleanupWorkflow:
    def test_has_steps(self):
        wf = create_cleanup_workflow()
        assert len(wf.steps) == 7


class TestFormatWorkflow:
    def test_basic(self):
        wf = create_standard_workflow()
        text = format_workflow(wf)
        assert "Standard Dedup" in text
        assert "scan" in text

    def test_with_completed(self):
        wf = create_standard_workflow()
        wf.steps[0].status = "completed"
        wf.current_step = 1
        text = format_workflow(wf)
        assert "[+]" in text
