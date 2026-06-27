"""File deduplication group comparison for DupeClean.

Compare two sets of duplicate groups to find changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupComparison:
    """Comparison between two sets of groups."""

    added: list[DuplicateGroup] = field(default_factory=list)
    removed: list[DuplicateGroup] = field(default_factory=list)
    unchanged: int = 0
    modified: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + self.modified

    @property
    def net_change(self) -> int:
        return len(self.added) - len(self.removed)


def compare_group_sets(
    old_groups: list[DuplicateGroup],
    new_groups: list[DuplicateGroup],
) -> GroupComparison:
    """Compare two sets of duplicate groups.

    Groups are matched by their hash value.
    """
    old_hashes = {g.hash_value: g for g in old_groups}
    new_hashes = {g.hash_value: g for g in new_groups}

    comparison = GroupComparison(
        added=[g for h, g in new_hashes.items() if h not in old_hashes],
        removed=[g for h, g in old_hashes.items() if h not in new_hashes],
        unchanged=sum(1 for h in new_hashes if h in old_hashes),
    )

    return comparison


def format_comparison(comparison: GroupComparison) -> str:
    """Format comparison as text."""
    lines = [
        "Group Comparison:",
        f"  Added: {len(comparison.added)}",
        f"  Removed: {len(comparison.removed)}",
        f"  Unchanged: {comparison.unchanged}",
        f"  Net: {comparison.net_change:+d}",
    ]

    if comparison.added:
        lines.append("\n  New groups:")
        for g in comparison.added[:10]:
            wasted = format_size(g.wasted_space)
            lines.append(f"    + {g.count} x {g.size_display} = {wasted} wasted")

    if comparison.removed:
        lines.append("\n  Removed groups:")
        for g in comparison.removed[:10]:
            lines.append(f"    - {g.count} x {g.size_display}")

    return "\n".join(lines)
