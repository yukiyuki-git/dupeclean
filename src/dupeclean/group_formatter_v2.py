"""File deduplication group formatter module for DupeClean.

Format duplicate groups in various output formats.
"""

from __future__ import annotations

import json

from .models import DuplicateGroup


def format_group_json(group: DuplicateGroup) -> dict:
    """Format a group as JSON-serializable dict."""
    return {
        "group_id": group.group_id,
        "hash": group.hash_value,
        "file_size": group.file_size,
        "wasted_space": group.wasted_space,
        "count": group.count,
        "files": [{"path": str(f.path), "size": f.size} for f in group.files],
    }


def format_groups_json(groups: list[DuplicateGroup]) -> str:
    """Format all groups as JSON."""
    return json.dumps([format_group_json(g) for g in groups], indent=2)


def format_group_table(groups: list[DuplicateGroup]) -> str:
    """Format groups as a table."""
    if not groups:
        return "No groups."

    lines = [
        f"{'#':>4} {'Files':>6} {'Size':>10} {'Wasted':>10} {'Hash':>12}",
        " " + "-" * 46,
    ]

    for g in groups[:30]:
        lines.append(
            f"{g.group_id:>4} {g.count:>6} "
            f"{g.size_display:>10} {g.wasted_display:>10} "
            f"{g.hash_value[:12]:>12}"
        )

    if len(groups) > 30:
        lines.append(f"\n  ... and {len(groups) - 30} more")

    return "\n".join(lines)


def format_group_tree(group: DuplicateGroup, indent: int = 2) -> str:
    """Format a group as a tree."""
    prefix = " " * indent
    lines = [
        f"{prefix}Group #{group.group_id} ({group.count} files, {group.wasted_display} wasted)"
    ]

    for i, fi in enumerate(group.files):
        connector = "├──" if i < len(group.files) - 1 else "└──"
        marker = "KEEP" if i == 0 else "DUP "
        lines.append(f"{prefix}  {connector} [{marker}] {fi.path.name}")

    return "\n".join(lines)


def format_group_summary_brief(group: DuplicateGroup) -> str:
    """Format a brief one-line summary of a group."""
    return (
        f"Group #{group.group_id}: "
        f"{group.count} x {group.size_display} = "
        f"{group.wasted_display} wasted"
    )
