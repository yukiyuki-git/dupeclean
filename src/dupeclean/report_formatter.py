"""File deduplication cleanup report formatter for DupeClean.

Format cleanup reports in multiple output formats.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .models import format_size


@dataclass
class ReportData:
    """Data for report generation."""

    operation_id: str
    files_processed: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    space_freed: int = 0
    errors: int = 0
    duration: float = 0.0
    strategy: str = "default"

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


def format_text_report(data: ReportData) -> str:
    """Format report as text."""
    return (
        f"Cleanup Report: {data.operation_id}\n"
        f"  Strategy: {data.strategy}\n"
        f"  Processed: {data.files_processed:,}\n"
        f"  Deleted: {data.files_deleted:,}\n"
        f"  Hardlinked: {data.files_hardlinked:,}\n"
        f"  Errors: {data.errors}\n"
        f"  Freed: {data.freed_display}\n"
        f"  Duration: {data.duration:.1f}s"
    )


def format_json_report(data: ReportData) -> str:
    """Format report as JSON."""
    return json.dumps(
        {
            "operation_id": data.operation_id,
            "strategy": data.strategy,
            "files_processed": data.files_processed,
            "files_deleted": data.files_deleted,
            "files_hardlinked": data.files_hardlinked,
            "space_freed": data.space_freed,
            "errors": data.errors,
            "duration": data.duration,
        },
        indent=2,
    )


def format_csv_report(data: ReportData) -> str:
    """Format report as CSV."""
    return (
        "operation_id,strategy,files_processed,files_deleted,"
        "files_hardlinked,space_freed,errors,duration\n"
        f"{data.operation_id},{data.strategy},{data.files_processed},"
        f"{data.files_deleted},{data.files_hardlinked},"
        f"{data.space_freed},{data.errors},{data.duration}"
    )


def format_html_report(data: ReportData) -> str:
    """Format report as HTML."""
    return f"""<!DOCTYPE html>
<html>
<head><title>DupeClean Report - {data.operation_id}</title></head>
<body>
<h1>Cleanup Report</h1>
<table>
<tr><td>Operation</td><td>{data.operation_id}</td></tr>
<tr><td>Strategy</td><td>{data.strategy}</td></tr>
<tr><td>Processed</td><td>{data.files_processed:,}</td></tr>
<tr><td>Deleted</td><td>{data.files_deleted:,}</td></tr>
<tr><td>Hardlinked</td><td>{data.files_hardlinked:,}</td></tr>
<tr><td>Errors</td><td>{data.errors}</td></tr>
<tr><td>Freed</td><td>{data.freed_display}</td></tr>
<tr><td>Duration</td><td>{data.duration:.1f}s</td></tr>
</table>
</body>
</html>"""


def format_markdown_report(data: ReportData) -> str:
    """Format report as Markdown."""
    return (
        f"# Cleanup Report: {data.operation_id}\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Strategy | {data.strategy} |\n"
        f"| Processed | {data.files_processed:,} |\n"
        f"| Deleted | {data.files_deleted:,} |\n"
        f"| Hardlinked | {data.files_hardlinked:,} |\n"
        f"| Errors | {data.errors} |\n"
        f"| Freed | {data.freed_display} |\n"
        f"| Duration | {data.duration:.1f}s |\n"
    )
