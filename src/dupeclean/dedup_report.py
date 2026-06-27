"""File deduplication report module for DupeClean.

Generate detailed dedup analysis reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class DedupReportSection:
    """A section of the dedup report."""

    title: str
    content: str
    priority: int = 0


@dataclass
class DedupReport:
    """Complete dedup analysis report."""

    title: str
    sections: list[DedupReportSection] = field(default_factory=list)

    def add_section(self, title: str, content: str, priority: int = 0) -> None:
        """Add a section to the report."""
        self.sections.append(
            DedupReportSection(
                title=title,
                content=content,
                priority=priority,
            )
        )

    def render(self) -> str:
        """Render the complete report as text."""
        self.sections.sort(key=lambda s: s.priority)
        lines = [self.title, "=" * len(self.title), ""]
        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)


def generate_dedup_report(
    groups: list[DuplicateGroup],
    total_files: int = 0,
    total_size: int = 0,
) -> DedupReport:
    """Generate a comprehensive dedup report."""
    report = DedupReport(title="DupeClean Dedup Report")

    # Summary section
    total_dupes = sum(g.count for g in groups)
    total_wasted = sum(g.wasted_space for g in groups)
    summary = (
        f"Total duplicate groups: {len(groups):,}\n"
        f"Total duplicate files: {total_dupes:,}\n"
        f"Total wasted space: {format_size(total_wasted)}\n"
    )
    if total_files > 0:
        pct = total_dupes / total_files * 100
        summary += f"Duplicate percentage: {pct:.1f}%\n"
    if total_size > 0:
        waste_pct = total_wasted / total_size * 100
        summary += f"Waste of total: {waste_pct:.1f}%\n"
    report.add_section("Summary", summary, priority=0)

    # Top groups by waste
    sorted_groups = sorted(groups, key=lambda g: g.wasted_space, reverse=True)
    if sorted_groups:
        top_lines = []
        for g in sorted_groups[:10]:
            top_lines.append(
                f"  Group #{g.group_id}: {g.count} x {g.size_display} = {g.wasted_display} wasted"
            )
            for fi in g.files[:3]:
                top_lines.append(f"    {fi.path}")
            if g.count > 3:
                top_lines.append(f"    ... and {g.count - 3} more")
        report.add_section(
            "Top Duplicate Groups",
            "\n".join(top_lines),
            priority=1,
        )

    # Size distribution
    if sorted_groups:
        dist_lines = []
        size_buckets = {
            "tiny (<1KB)": 0,
            "small (1-64KB)": 0,
            "medium (64KB-1MB)": 0,
            "large (1-16MB)": 0,
            "huge (>16MB)": 0,
        }
        for g in groups:
            if g.file_size < 1024:
                size_buckets["tiny (<1KB)"] += 1
            elif g.file_size < 65536:
                size_buckets["small (1-64KB)"] += 1
            elif g.file_size < 1048576:
                size_buckets["medium (64KB-1MB)"] += 1
            elif g.file_size < 16777216:
                size_buckets["large (1-16MB)"] += 1
            else:
                size_buckets["huge (>16MB)"] += 1

        for bucket, count in size_buckets.items():
            if count > 0:
                dist_lines.append(f"  {bucket}: {count} groups")
        if dist_lines:
            report.add_section(
                "Size Distribution",
                "\n".join(dist_lines),
                priority=2,
            )

    return report


def format_groups_table(groups: list[DuplicateGroup]) -> str:
    """Format groups as a table."""
    if not groups:
        return "No duplicate groups."

    lines = [
        f"{'#':>4s} {'Files':>6s} {'Size':>10s} {'Wasted':>10s} {'Hash':>12s}",
        " " + "-" * 48,
    ]

    for g in groups[:30]:
        lines.append(
            f"{g.group_id:>4d} {g.count:>6d} "
            f"{g.size_display:>10s} "
            f"{g.wasted_display:>10s} "
            f"{g.hash_value[:12]:>12s}"
        )

    if len(groups) > 30:
        lines.append(f"\n  ... and {len(groups) - 30} more groups")

    return "\n".join(lines)
