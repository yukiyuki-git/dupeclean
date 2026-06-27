"""File deduplication group reporter for DupeClean.

Generate detailed reports about duplicate group operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupReportData:
    """Data for group report generation."""

    groups: list[DuplicateGroup] = field(default_factory=list)
    total_files: int = 0
    total_size: int = 0
    scan_duration: float = 0.0
    cleanup_duration: float = 0.0
    files_cleaned: int = 0
    space_freed: int = 0

    @property
    def wasted_display(self) -> str:
        return format_size(sum(g.wasted_space for g in self.groups))


def generate_group_report_text(data: GroupReportData) -> str:
    """Generate text report."""
    lines = [
        "DupeClean Group Report",
        "=" * 22,
        "",
        f"Groups: {len(data.groups)}",
        f"Total files: {data.total_files:,}",
        f"Total size: {format_size(data.total_size)}",
        f"Wasted: {data.wasted_display}",
        f"Scan duration: {data.scan_duration:.2f}s",
    ]

    if data.files_cleaned > 0:
        lines.extend(
            [
                "",
                f"Files cleaned: {data.files_cleaned:,}",
                f"Space freed: {format_size(data.space_freed)}",
                f"Cleanup duration: {data.cleanup_duration:.2f}s",
            ]
        )

    return "\n".join(lines)


def generate_group_report_json(data: GroupReportData) -> str:
    """Generate JSON report."""
    return json.dumps(
        {
            "groups": len(data.groups),
            "total_files": data.total_files,
            "total_size": data.total_size,
            "wasted_space": sum(g.wasted_space for g in data.groups),
            "scan_duration": data.scan_duration,
            "files_cleaned": data.files_cleaned,
            "space_freed": data.space_freed,
        },
        indent=2,
    )


def format_group_report_data(data: GroupReportData) -> str:
    """Format report data as text."""
    return generate_group_report_text(data)
