"""File deduplication cleanup orchestrator for DupeClean.

Orchestrate the complete cleanup workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class CleanupStep:
    """A step in the cleanup workflow."""

    name: str
    status: str = "pending"  # pending, running, completed, failed
    result: dict = field(default_factory=dict)


@dataclass
class CleanupOrchestrator:
    """Orchestrate the complete cleanup workflow."""

    steps: list[CleanupStep] = field(default_factory=list)
    current_step: int = 0
    groups: list[DuplicateGroup] = field(default_factory=list)

    def add_step(self, name: str) -> None:
        self.steps.append(CleanupStep(name=name))

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

    def render(self) -> str:
        """Render orchestrator status."""
        status_icons = {
            "pending": "[ ]",
            "running": "[...]",
            "completed": "[+]",
            "failed": "[X]",
        }
        lines = [
            f"Cleanup Orchestrator: {self.progress:.0%} complete",
            "",
        ]
        for i, step in enumerate(self.steps):
            icon = status_icons.get(step.status, "[?]")
            marker = " -> " if i == self.current_step else "    "
            lines.append(f"  {marker}{icon} {step.name}")
        return "\n".join(lines)


def create_standard_orchestrator(
    groups: list[DuplicateGroup],
) -> CleanupOrchestrator:
    """Create a standard cleanup orchestrator."""
    orch = CleanupOrchestrator(groups=groups)
    orch.add_step("validate")
    orch.add_step("preview")
    orch.add_step("confirm")
    orch.add_step("execute")
    orch.add_step("verify")
    orch.add_step("report")
    return orch
