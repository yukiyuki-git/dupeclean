"""File deduplication group report for DupeClean.

Generate comprehensive reports about duplicate groups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupReportSection:
    """A section of the group report."""

    title: str
    content: str
    priority: int = 0


@dataclass
class GroupReport:
    """A comprehensive group report."""

    sections: list[GroupReportSection] = field(default_factory=list)
    generated_at: float = 0.0

    def add_section(self, title: str, content: str, priority: int = 0) -> None:
        self.sections.append(GroupReportSection(title=title, content=content, priority=priority))
        self.sections.sort(key=lambda s: s.priority)

    def render(self) -> str:
        lines = ["DupeClean Group Report", "=" * 22, ""]
        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)


def generate_group_report(groups: list[DuplicateGroup]) -> GroupReport:
    """Generate a comprehensive report about groups."""
    import time

    report = GroupReport(generated_at=time.time())

    # Summary
    total_wasted = sum(g.wasted_space for g in groups)
    total_files = sum(g.count for g in groups)
    report.add_section(
        "Summary",
        f"  Groups: {len(groups)}\n"
        f"  Total files: {total_files:,}\n"
        f"  Total wasted: {format_size(total_wasted)}",
        priority=0,
    )

    # Top groups
    sorted_groups = sorted(groups, key=lambda g: g.wasted_space, reverse=True)
    if sorted_groups:
        lines = []
        for g in sorted_groups[:10]:
            lines.append(
                f"  Group #{g.group_id}: {g.count} x {g.size_display} = {g.wasted_display} wasted"
            )
            for fi in g.files[:3]:
                lines.append(f"    {fi.path}")
        report.add_section("Top Groups", "\n".join(lines), priority=1)

    # Size distribution
    size_buckets = {"<1KB": 0, "1-64KB": 0, "64KB-1MB": 0, "1-16MB": 0, ">16MB": 0}
    for g in groups:
        if g.file_size < 1024:
            size_buckets["<1KB"] += 1
        elif g.file_size < 65536:
            size_buckets["1-64KB"] += 1
        elif g.file_size < 1048576:
            size_buckets["64KB-1MB"] += 1
        elif g.file_size < 16777216:
            size_buckets["1-16MB"] += 1
        else:
            size_buckets[">16MB"] += 1

    lines = []
    for bucket, count in size_buckets.items():
        if count > 0:
            lines.append(f"  {bucket}: {count} groups")
    if lines:
        report.add_section("Size Distribution", "\n".join(lines), priority=2)

    return report


def format_group_report(report: GroupReport) -> str:
    """Format report as text."""
    return report.render()
