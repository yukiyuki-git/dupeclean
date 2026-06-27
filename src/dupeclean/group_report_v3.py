"""File deduplication group report v3 for DupeClean.

Enhanced group reporting with interactive features.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class ReportSectionV2:
    """A report section with metadata."""

    title: str
    content: str
    section_type: str = "text"  # text, table, chart, summary
    priority: int = 0


@dataclass
class GroupReportV2:
    """Enhanced group report."""

    sections: list[ReportSectionV2] = field(default_factory=list)
    generated_at: float = 0.0

    def add_summary(self, title: str, content: str) -> None:
        self.sections.append(
            ReportSectionV2(title=title, content=content, section_type="summary", priority=0)
        )

    def add_table(self, title: str, headers: list[str], rows: list[list[str]]) -> None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        lines = []
        header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append("-" * len(header_line))
        for row in rows:
            lines.append(" | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)))

        self.sections.append(
            ReportSectionV2(title=title, content="\n".join(lines), section_type="table", priority=1)
        )

    def render(self) -> str:
        self.sections.sort(key=lambda s: s.priority)
        lines = ["DupeClean Report", "=" * 16, ""]
        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)


def generate_report_v2(groups: list[DuplicateGroup]) -> GroupReportV2:
    """Generate enhanced report from groups."""
    import time

    report = GroupReportV2(generated_at=time.time())

    total_wasted = sum(g.wasted_space for g in groups)
    total_files = sum(g.count for g in groups)
    report.add_summary(
        "Summary",
        f"  Groups: {len(groups)}\n  Files: {total_files:,}\n  Wasted: {format_size(total_wasted)}",
    )

    if groups:
        sorted_groups = sorted(groups, key=lambda g: g.wasted_space, reverse=True)
        headers = ["Group", "Files", "Size", "Wasted"]
        rows = []
        for g in sorted_groups[:20]:
            rows.append(
                [
                    str(g.group_id),
                    str(g.count),
                    g.size_display,
                    g.wasted_display,
                ]
            )
        report.add_table("Top Groups", headers, rows)

    return report


def format_report_v2(report: GroupReportV2) -> str:
    """Format report as text."""
    return report.render()
