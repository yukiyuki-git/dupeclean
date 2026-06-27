"""File deduplication group workflow module for DupeClean.

Orchestrate group operations as workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class WorkflowStage:
    """A stage in the group workflow."""

    name: str
    description: str
    status: str = "pending"
    result: dict = field(default_factory=dict)


@dataclass
class GroupWorkflow:
    """A workflow for processing duplicate groups."""

    name: str
    stages: list[WorkflowStage] = field(default_factory=list)
    current_stage: int = 0
    groups: list[DuplicateGroup] = field(default_factory=list)

    def add_stage(self, name: str, description: str) -> None:
        self.stages.append(WorkflowStage(name=name, description=description))

    @property
    def progress(self) -> float:
        if not self.stages:
            return 0.0
        completed = sum(1 for s in self.stages if s.status == "completed")
        return completed / len(self.stages)

    @property
    def is_complete(self) -> bool:
        return all(s.status == "completed" for s in self.stages)

    @property
    def current(self) -> WorkflowStage | None:
        if 0 <= self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        return None

    def advance(self) -> None:
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1

    def complete_current(self) -> None:
        if self.current:
            self.current.status = "completed"
            self.advance()

    def render(self) -> str:
        icons = {"pending": "[ ]", "running": "[...]", "completed": "[+]", "failed": "[X]"}
        lines = [f"Workflow: {self.name} ({self.progress:.0%})", ""]
        for i, stage in enumerate(self.stages):
            icon = icons.get(stage.status, "[?]")
            marker = " -> " if i == self.current_stage else "    "
            lines.append(f"  {marker}{icon} {stage.name}: {stage.description}")
        return "\n".join(lines)


def create_group_workflow(groups: list[DuplicateGroup]) -> GroupWorkflow:
    """Create a standard group processing workflow."""
    wf = GroupWorkflow(name="Group Processing", groups=groups)
    wf.add_stage("validate", "Validate all groups")
    wf.add_stage("filter", "Apply filters")
    wf.add_stage("sort", "Sort by priority")
    wf.add_stage("plan", "Create cleanup plan")
    wf.add_stage("preview", "Preview actions")
    wf.add_stage("execute", "Execute cleanup")
    wf.add_stage("verify", "Verify results")
    wf.add_stage("report", "Generate report")
    return wf
