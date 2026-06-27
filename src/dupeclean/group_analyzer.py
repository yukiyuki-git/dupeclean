"""File deduplication duplicate group analyzer for DupeClean.

Analyze duplicate groups for patterns and insights.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupPattern:
    """A pattern found in duplicate groups."""

    pattern_type: str  # "name", "extension", "size", "directory"
    value: str
    count: int = 0
    total_wasted: int = 0

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)


@dataclass
class GroupAnalysisV2:
    """Analysis of duplicate group patterns."""

    patterns: list[GroupPattern] = field(default_factory=list)
    total_groups: int = 0

    @property
    def top_pattern(self) -> GroupPattern | None:
        if not self.patterns:
            return None
        return max(self.patterns, key=lambda p: p.total_wasted)


def analyze_group_patterns(
    groups: list[DuplicateGroup],
) -> GroupAnalysisV2:
    """Analyze patterns in duplicate groups."""
    analysis = GroupAnalysisV2(total_groups=len(groups))

    ext_patterns: dict[str, GroupPattern] = {}
    size_patterns: dict[str, GroupPattern] = {}

    for group in groups:
        if not group.files:
            continue

        ext = group.files[0].ext.lower()
        if ext not in ext_patterns:
            ext_patterns[ext] = GroupPattern(pattern_type="extension", value=ext)
        ext_patterns[ext].count += 1
        ext_patterns[ext].total_wasted += group.wasted_space

        size_range = _get_size_range(group.file_size)
        if size_range not in size_patterns:
            size_patterns[size_range] = GroupPattern(pattern_type="size", value=size_range)
        size_patterns[size_range].count += 1
        size_patterns[size_range].total_wasted += group.wasted_space

    analysis.patterns.extend(ext_patterns.values())
    analysis.patterns.extend(size_patterns.values())
    analysis.patterns.sort(key=lambda p: p.total_wasted, reverse=True)

    return analysis


def _get_size_range(size: int) -> str:
    if size < 1024:
        return "<1KB"
    if size < 65536:
        return "1-64KB"
    if size < 1048566:
        return "64KB-1MB"
    if size < 16777216:
        return "1-16MB"
    return ">16MB"


def format_group_analysis(analysis: GroupAnalysisV2) -> str:
    """Format analysis as text."""
    lines = [
        f"Group Analysis: {analysis.total_groups} groups",
        "",
    ]

    for pattern in analysis.patterns[:15]:
        lines.append(
            f"  [{pattern.pattern_type}] {pattern.value}: "
            f"{pattern.count} groups, {pattern.wasted_display} wasted"
        )

    return "\n".join(lines)
