"""File deduplication cleanup reporter v3 for DupeClean.

Enhanced cleanup reporting with multiple output formats.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .models import format_size


@dataclass
class ReportDataV2:
    """Data for enhanced report generation."""

    operation_id: str
    files_processed: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    files_skipped: int = 0
    space_freed: int = 0
    errors: int = 0
    duration: float = 0.0
    strategy: str = "default"
    groups_processed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def success_rate(self) -> float:
        if self.files_processed == 0:
            return 0.0
        successful = self.files_deleted + self.files_hardlinked
        return successful / self.files_processed


def format_text_report_v2(data: ReportDataV2) -> str:
    """Format report as text."""
    return (
        f"Cleanup Report: {data.operation_id}\n"
        f"  Strategy: {data.strategy}\n"
        f"  Groups: {data.groups_processed}\n"
        f"  Processed: {data.files_processed:,}\n"
        f"  Deleted: {data.files_deleted:,}\n"
        f"  Hardlinked: {data.files_hardlinked:,}\n"
        f"  Skipped: {data.files_skipped:,}\n"
        f"  Errors: {data.errors}\n"
        f"  Freed: {data.freed_display}\n"
        f"  Duration: {data.duration:.1f}s\n"
        f"  Success rate: {data.success_rate:.1%}"
    )


def format_json_report_v2(data: ReportDataV2) -> str:
    """Format report as JSON."""
    return json.dumps(
        {
            "operation_id": data.operation_id,
            "strategy": data.strategy,
            "groups_processed": data.groups_processed,
            "files_processed": data.files_processed,
            "files_deleted": data.files_deleted,
            "files_hardlinked": data.files_hardlinked,
            "files_skipped": data.files_skipped,
            "space_freed": data.space_freed,
            "errors": data.errors,
            "duration": data.duration,
            "success_rate": data.success_rate,
        },
        indent=2,
    )


def format_markdown_report_v2(data: ReportDataV2) -> str:
    """Format report as Markdown."""
    return (
        f"# Cleanup Report: {data.operation_id}\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Strategy | {data.strategy} |\n"
        f"| Groups | {data.groups_processed} |\n"
        f"| Processed | {data.files_processed:,} |\n"
        f"| Deleted | {data.files_deleted:,} |\n"
        f"| Hardlinked | {data.files_hardlinked:,} |\n"
        f"| Freed | {data.freed_display} |\n"
        f"| Duration | {data.duration:.1f}s |\n"
        f"| Success Rate | {data.success_rate:.1%} |\n"
    )
