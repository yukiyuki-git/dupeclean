"""Duplicate file consolidation module for DupeClean.

Consolidates duplicate files by:
- Moving all duplicates to a single directory
- Creating symlinks/hardlinks to the original
- Generating a dedup report
"""

from __future__ import annotations

from dataclasses import dataclass

from .cleanup import CleanupManager
from .models import (
    CleanupAction,
    CleanupResult,
    DuplicateGroup,
    format_size,
)
from .utils import create_hardlink


@dataclass
class ConsolidationPlan:
    """Plan for consolidating duplicate files."""

    groups: list[DuplicateGroup]
    total_duplicates: int = 0
    total_wasted: int = 0
    keep_strategy: str = "shortest_path"

    def __post_init__(self) -> None:
        self.total_duplicates = sum(g.count - 1 for g in self.groups)
        self.total_wasted = sum(g.wasted_space for g in self.groups)

    @property
    def summary(self) -> str:
        return (
            f"{len(self.groups)} groups, "
            f"{self.total_duplicates} files to process, "
            f"{format_size(self.total_wasted)} savings"
        )


def create_plan(
    groups: list[DuplicateGroup],
    strategy: str = "shortest_path",
) -> ConsolidationPlan:
    """Create a consolidation plan from duplicate groups.

    Args:
        groups: Duplicate groups from analysis.
        strategy: How to choose which file to keep.
            "shortest_path" — keep file with shortest path
            "newest" — keep newest file
            "oldest" — keep oldest file

    Returns:
        ConsolidationPlan with action details.
    """
    plan = ConsolidationPlan(groups=groups, keep_strategy=strategy)
    return plan


def execute_consolidation(
    plan: ConsolidationPlan,
    method: str = "hardlink",
    dry_run: bool = True,
) -> list[CleanupResult]:
    """Execute a consolidation plan.

    Args:
        plan: The consolidation plan.
        method: "hardlink", "delete", or "move".
        dry_run: If True, don't actually modify files.

    Returns:
        List of CleanupResult per group.
    """
    action_map = {
        "hardlink": CleanupAction.HARDLINK,
        "delete": CleanupAction.DELETE,
        "move": CleanupAction.MOVE,
    }
    action = action_map.get(method, CleanupAction.HARDLINK)

    manager = CleanupManager(dry_run=dry_run)
    result = manager.execute_cleanup(plan.groups, action)
    return [result]


def hardlink_duplicates(
    groups: list[DuplicateGroup],
    dry_run: bool = True,
) -> int:
    """Replace duplicate files with hard links to the original.

    Returns count of files hardlinked.
    """
    count = 0
    for group in groups:
        if len(group.files) < 2:
            continue
        original = group.files[0]  # Keep first as original
        for dupe in group.files[1:]:
            if dry_run:
                count += 1
                continue
            success, _ = create_hardlink(original.path, dupe.path)
            if success:
                count += 1
    return count


def format_plan(plan: ConsolidationPlan) -> str:
    """Format a consolidation plan as text."""
    lines = [
        "Consolidation Plan:",
        f"  Strategy: {plan.keep_strategy}",
        f"  Groups: {len(plan.groups)}",
        f"  Files to process: {plan.total_duplicates}",
        f"  Potential savings: {format_size(plan.total_wasted)}",
        "",
    ]

    for group in plan.groups[:10]:
        keep = group.files[0]
        lines.append(f"  Group #{group.group_id}: {group.count} x {group.size_display}")
        lines.append(f"    KEEP: {keep.path}")
        for dupe in group.files[1:]:
            lines.append(f"    LINK: {dupe.path}")

    if len(plan.groups) > 10:
        lines.append(f"\n  ... and {len(plan.groups) - 10} more groups")

    return "\n".join(lines)
