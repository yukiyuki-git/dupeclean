"""File deduplication dry-run module for DupeClean.

Preview cleanup operations without executing them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size


@dataclass
class DryRunAction:
    """A previewed cleanup action."""

    action_type: str
    source: Path
    target: Path | None = None
    size: int = 0
    reason: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class DryRunResult:
    """Result of a dry-run preview."""

    actions: list[DryRunAction] = field(default_factory=list)
    total_actions: int = 0
    total_savings: int = 0

    @property
    def savings_display(self) -> str:
        return format_size(self.total_savings)


def preview_cleanup(
    groups: list[DuplicateGroup],
    strategy: str = "keep_shortest",
) -> DryRunResult:
    """Preview cleanup actions without executing.

    Args:
        groups: Duplicate groups to preview.
        strategy: Keep strategy.

    Returns:
        DryRunResult with all previewed actions.
    """
    result = DryRunResult()

    for group in groups:
        if len(group.files) < 2:
            continue

        keep_idx = _select_keeper(group, strategy)
        keeper = group.files[keep_idx]

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue

            result.actions.append(
                DryRunAction(
                    action_type="delete",
                    source=fi.path,
                    target=keeper.path,
                    size=fi.size,
                    reason=f"Duplicate of {keeper.path.name}",
                )
            )
            result.total_savings += fi.size

    result.total_actions = len(result.actions)
    return result


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    """Select which file to keep."""
    if strategy == "keep_newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "keep_oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    # Default: keep shortest path
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_dry_run(result: DryRunResult) -> str:
    """Format dry-run result as text."""
    if not result.actions:
        return "No actions to preview."

    lines = [
        f"Dry Run Preview: {result.total_actions} actions, {result.savings_display} savings",
        "",
    ]

    for action in result.actions[:20]:
        lines.append(
            f"  {action.action_type}: {action.source.name} "
            f"({action.size_display}) - {action.reason}"
        )

    if result.total_actions > 20:
        lines.append(f"\n  ... and {result.total_actions - 20} more")

    return "\n".join(lines)
