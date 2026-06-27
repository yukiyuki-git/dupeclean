"""File deduplication cleanup workflow step module for DupeClean.

Define and manage cleanup workflow steps.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorkflowStepDef:
    """Definition of a workflow step."""

    name: str
    description: str
    required: bool = True
    timeout: float = 300.0


# Built-in workflow steps
WORKFLOW_STEPS = {
    "scan": WorkflowStepDef(
        name="Scan",
        description="Scan directory tree for files",
        required=True,
    ),
    "analyze": WorkflowStepDef(
        name="Analyze",
        description="Analyze files for duplicates",
        required=True,
    ),
    "validate": WorkflowStepDef(
        name="Validate",
        description="Validate cleanup plan",
        required=True,
    ),
    "preview": WorkflowStepDef(
        name="Preview",
        description="Preview cleanup actions",
        required=False,
    ),
    "confirm": WorkflowStepDef(
        name="Confirm",
        description="Confirm cleanup execution",
        required=True,
    ),
    "execute": WorkflowStepDef(
        name="Execute",
        description="Execute cleanup actions",
        required=True,
    ),
    "verify": WorkflowStepDef(
        name="Verify",
        description="Verify cleanup results",
        required=False,
    ),
    "report": WorkflowStepDef(
        name="Report",
        description="Generate cleanup report",
        required=False,
    ),
}


def get_step(name: str) -> WorkflowStepDef:
    """Get a workflow step by name."""
    return WORKFLOW_STEPS.get(name, WorkflowStepDef(name=name, description=f"Custom step: {name}"))


def list_steps() -> list[WorkflowStepDef]:
    """List all workflow steps."""
    return list(WORKFLOW_STEPS.values())


def format_step(step: WorkflowStepDef) -> str:
    """Format workflow step as text."""
    req = "Required" if step.required else "Optional"
    return f"  {step.name}: {step.description} [{req}]"
