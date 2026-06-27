"""File deduplication duplicate group formatter for DupeClean.

Format duplicate groups for display.
"""

from __future__ import annotations

from .models import DuplicateGroup, format_size


def format_group_detail(group: DuplicateGroup) -> str:
    """Format a single group with full detail."""
    lines = [
        f"Group #{group.group_id}:",
        f"  Files: {group.count}",
        f"  Size: {group.size_display}",
        f"  Wasted: {group.wasted_display}",
        f"  Hash: {group.hash_value[:16]}...",
        "",
    ]

    for i, fi in enumerate(group.files):
        marker = "[KEEP]" if i == 0 else "[DUP]"
        lines.append(f"  {marker} {fi.path}")
        lines.append(f"         {fi.size_display}")

    return "\n".join(lines)


def format_group_list(groups: list[DuplicateGroup]) -> str:
    """Format a list of groups as summary."""
    if not groups:
        return "No duplicate groups."

    total_wasted = sum(g.wasted_space for g in groups)
    lines = [
        f"Duplicate Groups: {len(groups)}",
        f"Total wasted: {format_size(total_wasted)}",
        "",
        f"{'#':>4} {'Files':>6} {'Size':>10} {'Wasted':>10}",
        " " + "-" * 34,
    ]

    for g in groups[:30]:
        lines.append(f"{g.group_id:>4} {g.count:>6} {g.size_display:>10} {g.wasted_display:>10}")

    if len(groups) > 30:
        lines.append(f"\n  ... and {len(groups) - 30} more")

    return "\n".join(lines)


def format_group_tree(group: DuplicateGroup, indent: int = 2) -> str:
    """Format a group as a tree structure."""
    prefix = " " * indent
    lines = [
        f"{prefix}├─ Group #{group.group_id} ({group.count} files, {group.wasted_display} wasted)"
    ]

    for i, fi in enumerate(group.files):
        connector = "├─" if i < len(group.files) - 1 else "└─"
        marker = "KEEP" if i == 0 else "DUP "
        lines.append(f"{prefix}  {connector} [{marker}] {fi.path.name}")

    return "\n".join(lines)
