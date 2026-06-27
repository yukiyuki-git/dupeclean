"""File deduplication group formatter v3 for DupeClean.

Enhanced group formatting with rich output.
"""

from __future__ import annotations

import json

from .models import DuplicateGroup


def format_group_rich(group: DuplicateGroup, width: int = 60) -> str:
    """Format group with rich visual elements."""
    bar_width = min(width - 20, 40)
    waste_pct = min(100, (group.wasted_space / (group.file_size * group.count)) * 100)
    filled = int(waste_pct / 100 * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)

    lines = [
        f"  Group #{group.group_id} [{bar}] {waste_pct:.0f}% waste",
        f"    {group.count} files x {group.size_display} = {group.wasted_display} wasted",
    ]

    for i, fi in enumerate(group.files):
        marker = "★" if i == 0 else "✗"
        lines.append(f"    {marker} {fi.path.name}")

    return "\n".join(lines)


def format_groups_compact(groups: list[DuplicateGroup]) -> str:
    """Format groups in compact one-line-per-group format."""
    if not groups:
        return "No duplicate groups."

    lines = [
        f"{'#':>4} {'Files':>6} {'Size':>10} {'Wasted':>10} {'Impact':>8}",
        " " + "-" * 42,
    ]

    for g in groups[:30]:
        if g.wasted_space > 1_000_000:
            impact = "HIGH"
        elif g.wasted_space > 10_000:
            impact = "MED"
        else:
            impact = "LOW"
        lines.append(
            f"{g.group_id:>4} {g.count:>6} {g.size_display:>10} {g.wasted_display:>10} {impact:>8}"
        )

    if len(groups) > 30:
        lines.append(f"\n  ... and {len(groups) - 30} more")

    return "\n".join(lines)


def format_groups_json_compact(groups: list[DuplicateGroup]) -> str:
    """Format groups as compact JSON."""
    data = [
        {
            "id": g.group_id,
            "n": g.count,
            "sz": g.file_size,
            "w": g.wasted_space,
            "f": [str(fi.path) for fi in g.files[:3]],
        }
        for g in groups[:50]
    ]
    return json.dumps(data)
