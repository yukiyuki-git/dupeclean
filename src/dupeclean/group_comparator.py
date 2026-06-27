"""File deduplication duplicate group comparator for DupeClean.

Compare duplicate groups between scans.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class GroupDiff:
    """Difference between two sets of duplicate groups."""

    added: list[DuplicateGroup] = field(default_factory=list)
    removed: list[DuplicateGroup] = field(default_factory=list)
    unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed)

    @property
    def net_change(self) -> int:
        return len(self.added) - len(self.removed)


def compare_groups(
    old_groups: list[DuplicateGroup],
    new_groups: list[DuplicateGroup],
) -> GroupDiff:
    """Compare two sets of duplicate groups."""
    old_hashes = {g.hash_value: g for g in old_groups}
    new_hashes = {g.hash_value: g for g in new_groups}

    diff = GroupDiff(
        added=[g for h, g in new_hashes.items() if h not in old_hashes],
        removed=[g for h, g in old_hashes.items() if h not in new_hashes],
        unchanged=len([h for h in new_hashes if h in old_hashes]),
    )

    return diff


def format_group_diff(diff: GroupDiff) -> str:
    """Format group diff as text."""
    lines = [
        "Group Diff:",
        f"  Added: {len(diff.added)}",
        f"  Removed: {len(diff.removed)}",
        f"  Unchanged: {diff.unchanged}",
        f"  Net: {diff.net_change:+d}",
    ]

    if diff.added:
        lines.append("\n  New groups:")
        for g in diff.added[:10]:
            lines.append(f"    + {g.count} x {g.size_display} = {g.wasted_display} wasted")

    if diff.removed:
        lines.append("\n  Removed groups:")
        for g in diff.removed[:10]:
            lines.append(f"    - {g.count} x {g.size_display}")

    return "\n".join(lines)
