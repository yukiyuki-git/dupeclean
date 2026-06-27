"""File deduplication diff module for DupeClean.

Compare dedup results between two scans.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class DedupDiff:
    """Difference between two dedup results."""

    old_groups: int = 0
    new_groups: int = 0
    added_groups: list[DuplicateGroup] = field(default_factory=list)
    removed_groups: list[DuplicateGroup] = field(default_factory=list)
    unchanged_groups: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added_groups) + len(self.removed_groups)

    @property
    def net_change(self) -> int:
        return self.new_groups - self.old_groups


def diff_dedup_results(
    old_groups: list[DuplicateGroup],
    new_groups: list[DuplicateGroup],
) -> DedupDiff:
    """Compare two sets of duplicate groups.

    Groups are matched by their hash values.
    """
    old_hashes = {g.hash_value: g for g in old_groups}
    new_hashes = {g.hash_value: g for g in new_groups}

    added = [g for h, g in new_hashes.items() if h not in old_hashes]
    removed = [g for h, g in old_hashes.items() if h not in new_hashes]
    unchanged = len([h for h in new_hashes if h in old_hashes])

    return DedupDiff(
        old_groups=len(old_groups),
        new_groups=len(new_groups),
        added_groups=added,
        removed_groups=removed,
        unchanged_groups=unchanged,
    )


def format_dedup_diff(diff: DedupDiff) -> str:
    """Format dedup diff as text."""
    lines = [
        "Dedup Diff:",
        f"  Old groups: {diff.old_groups:,}",
        f"  New groups: {diff.new_groups:,}",
        f"  Net change: {diff.net_change:+d}",
        f"  Added: {len(diff.added_groups):,}",
        f"  Removed: {len(diff.removed_groups):,}",
        f"  Unchanged: {diff.unchanged_groups:,}",
    ]

    if diff.added_groups:
        lines.append("\n  New duplicate groups:")
        for g in diff.added_groups[:10]:
            lines.append(f"    + {g.count} x {g.size_display} = {g.wasted_display} wasted")

    if diff.removed_groups:
        lines.append("\n  Removed groups:")
        for g in diff.removed_groups[:10]:
            lines.append(f"    - {g.count} x {g.size_display}")

    return "\n".join(lines)
