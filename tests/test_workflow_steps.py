"""Tests for DupeClean workflow steps module."""

from __future__ import annotations

from dupeclean.workflow_steps import (
    WORKFLOW_STEPS,
    WorkflowStepDef,
    format_step,
    get_step,
    list_steps,
)


class TestGetStep:
    def test_scan(self):
        step = get_step("scan")
        assert step.name == "Scan"
        assert step.required is True

    def test_unknown(self):
        step = get_step("custom")
        assert step.name == "custom"


class TestListSteps:
    def test_has_steps(self):
        steps = list_steps()
        assert len(steps) >= 8


class TestWorkflowSteps:
    def test_all_exist(self):
        expected = {
            "scan",
            "analyze",
            "validate",
            "preview",
            "confirm",
            "execute",
            "verify",
            "report",
        }
        assert set(WORKFLOW_STEPS.keys()) == expected


class TestFormatStep:
    def test_required(self):
        step = get_step("scan")
        text = format_step(step)
        assert "Required" in text

    def test_optional(self):
        step = get_step("preview")
        text = format_step(step)
        assert "Optional" in text


class TestWorkflowStepDef:
    def test_defaults(self):
        step = WorkflowStepDef(name="test", description="test")
        assert step.required is True
        assert step.timeout == 300.0
