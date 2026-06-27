"""File deduplication reporting module for DupeClean.

Generate comprehensive dedup reports in multiple formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class ReportSection:
    """A section of a dedup report."""

    title: str
    content: str
    section_type: str = "text"  # text, table, chart


@dataclass
class DedupReportV2:
    """Comprehensive dedup report."""

    title: str
    generated_at: float = 0.0
    sections: list[ReportSection] = field(default_factory=list)

    def add_text(self, title: str, content: str) -> None:
        self.sections.append(ReportSection(title=title, content=content))

    def add_table(self, title: str, headers: list[str], rows: list[list[str]]) -> None:
        """Add a table section."""
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
            ReportSection(
                title=title,
                content="\n".join(lines),
                section_type="table",
            )
        )

    def render(self) -> str:
        """Render the complete report."""
        lines = [
            self.title,
            "=" * len(self.title),
            "",
        ]

        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.content)
            lines.append("")

        return "\n".join(lines)


def generate_full_report(
    groups: list[DuplicateGroup],
    total_files: int = 0,
    total_size: int = 0,
) -> DedupReportV2:
    """Generate a comprehensive dedup report."""
    import time

    report = DedupReportV2(
        title="DupeClean Comprehensive Report",
        generated_at=time.time(),
    )

    # Summary
    total_dupes = sum(g.count for g in groups)
    total_wasted = sum(g.wasted_space for g in groups)
    report.add_text(
        "Summary",
        f"Total files: {total_files:,}\n"
        f"Total size: {format_size(total_size)}\n"
        f"Duplicate groups: {len(groups):,}\n"
        f"Duplicate files: {total_dupes:,}\n"
        f"Wasted space: {format_size(total_wasted)}",
    )

    # Top groups table
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
        report.add_table("Top Duplicate Groups", headers, rows)

    return report


def format_report(report: DedupReportV2) -> str:
    """Format report as text."""
    return report.render()
