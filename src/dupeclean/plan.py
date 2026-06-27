"""File deduplication cleanup plan module for DupeClean.

Create comprehensive cleanup plans from analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size


@dataclass
class PlanAction:
    """A single action in a cleanup plan."""

    action_type: str
    source: Path
    target: Path | None = None
    size: int = 0
    reason: str = ""
    priority: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupPlan:
    """A comprehensive cleanup plan."""

    name: str
    actions: list[PlanAction] = field(default_factory=list)
    strategy: str = "shortest"

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    @property
    def total_savings(self) -> int:
        return sum(a.size for a in self.actions)

    @property
    def savings_display(self) -> str:
        return format_size(self.total_savings)

    def add(self, action: PlanAction) -> None:
        self.actions.append(action)
        self.actions.sort(key=lambda a: a.priority, reverse=True)

    def render(self) -> str:
        """Render plan as text."""
        lines = [
            f"Cleanup Plan: {self.name}",
            f"  Strategy: {self.strategy}",
            f"  Actions: {self.total_actions}",
            f"  Savings: {self.savings_display}",
            "",
        ]
        for action in self.actions[:20]:
            lines.append(
                f"  [{action.action_type}] {action.source.name} "
                f"({action.size_display}) - {action.reason}"
            )
        if self.total_actions > 20:
            lines.append(f"\n  ... and {self.total_actions - 20} more")
        return "\n".join(lines)


def create_cleanup_plan(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
    name: str = "Auto-generated",
) -> CleanupPlan:
    """Create a cleanup plan from duplicate groups."""
    plan = CleanupPlan(name=name, strategy=strategy)

    for group in groups:
        if len(group.files) < 2:
            continue

        keep_idx = _select_keeper(group, strategy)
        keeper = group.files[keep_idx]

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue
            plan.add(
                PlanAction(
                    action_type="delete",
                    source=fi.path,
                    target=keeper.path,
                    size=fi.size,
                    reason=f"Duplicate of {keeper.path.name}",
                    priority=group.file_size,
                )
            )

    return plan


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))
