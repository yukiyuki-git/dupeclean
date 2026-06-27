"""File deduplication cleanup workflow for DupeClean.

Complete cleanup workflow from analysis to execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    """A step in the cleanup workflow."""

    name: str
    status: str = "pending"
    result: dict = field(default_factory=dict)


@dataclass
class CleanupWorkflow:
    """Complete cleanup workflow."""

    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    current_step: int = 0

    def add_step(self, name: str) -> None:
        self.steps.append(WorkflowStep(name=name))

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
    def current(self) -> WorkflowStep | None:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def advance(self) -> None:
        """Move to next step."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1

    def complete_current(self) -> None:
        """Mark current step as completed."""
        if self.current:
            self.current.status = "completed"
            self.advance()

    def fail_current(self, error: str = "") -> None:
        """Mark current step as failed."""
        if self.current:
            self.current.status = "failed"
            self.current.result["error"] = error

    def render(self) -> str:
        """Render workflow status."""
        status_icons = {
            "pending": "[ ]",
            "running": "[...]",
            "completed": "[+]",
            "failed": "[X]",
        }
        lines = [
            f"Workflow: {self.name} ({self.progress:.0%})",
            "",
        ]
        for i, step in enumerate(self.steps):
            icon = status_icons.get(step.status, "[?]")
            marker = " -> " if i == self.current_step else "    "
            lines.append(f"  {marker}{icon} {step.name}")
        return "\n".join(lines)


def create_cleanup_workflow() -> CleanupWorkflow:
    """Create a standard cleanup workflow."""
    wf = CleanupWorkflow(name="Standard Cleanup")
    wf.add_step("scan")
    wf.add_step("analyze")
    wf.add_step("validate")
    wf.add_step("preview")
    wf.add_step("execute")
    wf.add_step("verify")
    wf.add_step("report")
    return wf
