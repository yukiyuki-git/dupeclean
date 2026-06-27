"""File deduplication cleanup plan v2 for DupeClean.

Enhanced cleanup planning with detailed actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size


@dataclass
class PlanActionV2:
    """A detailed cleanup action."""

    action_type: str
    source: Path
    target: Path | None = None
    size: int = 0
    reason: str = ""
    priority: int = 0
    group_id: int = -1

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupPlanV2:
    """A detailed cleanup plan."""

    name: str
    actions: list[PlanActionV2] = field(default_factory=list)
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

    def add(self, action: PlanActionV2) -> None:
        self.actions.append(action)
        self.actions.sort(key=lambda a: a.priority, reverse=True)


def create_plan_v2(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
    name: str = "Auto-generated",
) -> CleanupPlanV2:
    """Create a detailed cleanup plan."""
    plan = CleanupPlanV2(name=name, strategy=strategy)

    for group in groups:
        if len(group.files) < 2:
            continue

        keep_idx = _select_keeper(group, strategy)
        keeper = group.files[keep_idx]

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue
            plan.add(
                PlanActionV2(
                    action_type="delete",
                    source=fi.path,
                    target=keeper.path,
                    size=fi.size,
                    reason=f"Duplicate of {keeper.path.name}",
                    priority=group.file_size,
                    group_id=group.group_id,
                )
            )

    return plan


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_plan_v2(plan: CleanupPlanV2) -> str:
    """Format plan as text."""
    lines = [
        f"Cleanup Plan: {plan.name}",
        f"  Strategy: {plan.strategy}",
        f"  Actions: {plan.total_actions}",
        f"  Savings: {plan.savings_display}",
        "",
    ]
    for action in plan.actions[:20]:
        lines.append(
            f"  [{action.action_type}] {action.source.name} "
            f"({action.size_display}) - {action.reason}"
        )
    if plan.total_actions > 20:
        lines.append(f"\n  ... and {plan.total_actions - 20} more")
    return "\n".join(lines)
