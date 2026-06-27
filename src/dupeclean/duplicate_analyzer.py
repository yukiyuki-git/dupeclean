"""File deduplication duplicate analyzer for DupeClean.

Analyze duplicate groups for insights and patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupAnalysis:
    """Analysis of a duplicate group."""

    group_id: int
    file_count: int
    file_size: int
    wasted_space: int
    extensions: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)


@dataclass
class DuplicateAnalysis:
    """Complete duplicate analysis."""

    total_groups: int = 0
    total_files: int = 0
    total_wasted: int = 0
    largest_group: int = 0
    largest_waste: int = 0
    most_common_ext: str = ""
    groups: list[GroupAnalysis] = field(default_factory=list)

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)


def analyze_duplicates(
    groups: list[DuplicateGroup],
) -> DuplicateAnalysis:
    """Analyze duplicate groups for insights."""
    analysis = DuplicateAnalysis(
        total_groups=len(groups),
        total_files=sum(g.count for g in groups),
        total_wasted=sum(g.wasted_space for g in groups),
    )

    ext_counts: dict[str, int] = {}

    for group in groups:
        analysis.largest_group = max(analysis.largest_group, group.count)
        analysis.largest_waste = max(analysis.largest_waste, group.wasted_space)

        ext = group.files[0].ext if group.files else ""
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

        analysis.groups.append(
            GroupAnalysis(
                group_id=group.group_id,
                file_count=group.count,
                file_size=group.file_size,
                wasted_space=group.wasted_space,
                extensions=[ext],
                paths=[str(f.path) for f in group.files[:5]],
            )
        )

    if ext_counts:
        analysis.most_common_ext = max(ext_counts, key=ext_counts.get)

    return analysis


def format_analysis(analysis: DuplicateAnalysis) -> str:
    """Format analysis as text."""
    lines = [
        "Duplicate Analysis:",
        f"  Groups: {analysis.total_groups:,}",
        f"  Files: {analysis.total_files:,}",
        f"  Wasted: {analysis.wasted_display}",
        f"  Largest group: {analysis.largest_group} files",
        f"  Most common: .{analysis.most_common_ext}",
    ]

    for group in analysis.groups[:10]:
        lines.append(
            f"  Group #{group.group_id}: "
            f"{group.file_count} x {format_size(group.file_size)} "
            f"= {format_size(group.wasted_space)} wasted"
        )

    return "\n".join(lines)
