"""File deduplication duplicate group export for DupeClean.

Export duplicate groups in various formats.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from .models import DuplicateGroup, format_size


def export_groups_json(groups: list[DuplicateGroup]) -> str:
    """Export groups as JSON."""
    data = [
        {
            "group_id": g.group_id,
            "hash": g.hash_value,
            "file_size": g.file_size,
            "wasted_space": g.wasted_space,
            "count": g.count,
            "files": [str(f.path) for f in g.files],
        }
        for g in groups
    ]
    return json.dumps(data, indent=2)


def export_groups_csv(groups: list[DuplicateGroup]) -> str:
    """Export groups as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["group_id", "hash", "file_size", "wasted_space", "count", "file_path"])
    for g in groups:
        for fi in g.files:
            writer.writerow(
                [
                    g.group_id,
                    g.hash_value,
                    g.file_size,
                    g.wasted_space,
                    g.count,
                    str(fi.path),
                ]
            )
    return output.getvalue()


def export_groups_text(groups: list[DuplicateGroup]) -> str:
    """Export groups as formatted text."""
    if not groups:
        return "No duplicate groups."

    total_wasted = sum(g.wasted_space for g in groups)
    lines = [
        f"Duplicate Groups: {len(groups)}",
        f"Total wasted: {format_size(total_wasted)}",
        "",
    ]

    for g in groups:
        lines.append(f"Group #{g.group_id}: {g.count} files x {g.size_display}")
        for fi in g.files:
            lines.append(f"  {fi.path}")
        lines.append("")

    return "\n".join(lines)


def save_groups(
    groups: list[DuplicateGroup],
    path: Path,
    format: str = "json",
) -> None:
    """Save groups to file."""
    if format == "json":
        content = export_groups_json(groups)
    elif format == "csv":
        content = export_groups_csv(groups)
    else:
        content = export_groups_text(groups)

    path.write_text(content, encoding="utf-8")


def format_export_summary(
    groups: list[DuplicateGroup],
    path: Path,
    format: str,
) -> str:
    """Format export summary as text."""
    total_wasted = sum(g.wasted_space for g in groups)
    return (
        f"Exported {len(groups)} groups to {path} ({format})\n"
        f"  Total wasted: {format_size(total_wasted)}"
    )
