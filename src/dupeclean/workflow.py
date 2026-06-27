"""File deduplication workflow module for DupeClean.

Orchestrate complete dedup workflows end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """A step in a dedup workflow."""

    name: str
    action: str
    status: str = "pending"  # pending, running, completed, failed
    result: dict = field(default_factory=dict)


@dataclass
class Workflow:
    """A complete dedup workflow."""

    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    current_step: int = 0
    status: str = "idle"  # idle, running, completed, failed

    def add_step(self, name: str, action: str) -> None:
        self.steps.append(WorkflowStep(name=name, action=action))

    @property
    def progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == "completed")
        return completed / len(self.steps)

    @property
    def is_complete(self) -> bool:
        return all(s.status == "completed" for s in self.steps)

    @property
    def has_failures(self) -> bool:
        return any(s.status == "failed" for s in self.steps)


def create_standard_workflow() -> Workflow:
    """Create the standard dedup workflow."""
    workflow = Workflow(name="Standard Dedup")
    workflow.add_step("scan", "Scan directory tree")
    workflow.add_step("size_filter", "Filter by file size")
    workflow.add_step("quick_hash", "Quick hash matching")
    workflow.add_step("full_hash", "Full hash verification")
    workflow.add_step("report", "Generate report")
    return workflow


def create_quick_workflow() -> Workflow:
    """Create a quick scan workflow (no hashing)."""
    workflow = Workflow(name="Quick Scan")
    workflow.add_step("scan", "Scan directory tree")
    workflow.add_step("size_group", "Group by size")
    workflow.add_step("report", "Generate report")
    return workflow


def create_cleanup_workflow() -> Workflow:
    """Create a full cleanup workflow."""
    workflow = Workflow(name="Full Cleanup")
    workflow.add_step("scan", "Scan directory tree")
    workflow.add_step("dedup", "Find duplicates")
    workflow.add_step("verify", "Verify findings")
    workflow.add_step("plan", "Create cleanup plan")
    workflow.add_step("execute", "Execute cleanup")
    workflow.add_step("verify_cleanup", "Verify cleanup")
    workflow.add_step("report", "Generate report")
    return workflow


def format_workflow(workflow: Workflow) -> str:
    """Format workflow status as text."""
    status_icons = {
        "pending": "[ ]",
        "running": "[...]",
        "completed": "[+]",
        "failed": "[X]",
    }

    lines = [
        f"Workflow: {workflow.name} ({workflow.status}) [{workflow.progress:.0%}]",
        "",
    ]

    for i, step in enumerate(workflow.steps):
        icon = status_icons.get(step.status, "[?]")
        marker = " -> " if i == workflow.current_step else "    "
        lines.append(f"  {marker}{icon} {step.name}: {step.action}")

    return "\n".join(lines)
