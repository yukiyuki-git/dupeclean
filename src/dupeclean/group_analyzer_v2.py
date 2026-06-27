"""File deduplication group analyzer v2 for DupeClean.

Enhanced group analysis with deeper insights.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class GroupInsight:
    """An insight about a group."""
    group_id: int
    insight_type: str  # "pattern", "anomaly", "optimization"
    title: str
    description: str
    severity: str = "info"


@dataclass
class GroupAnalysisResult:
    """Result of enhanced group analysis."""
    insights: list[GroupInsight] = field(default_factory=list)
    patterns: dict[str, int] = field(default_factory=dict)

    @property
    def insight_count(self) -> int:
        return len(self.insights)

    @property
    def has_insights(self) -> bool:
        return len(self.insights) > 0


def analyze_group_patterns(groups: list[DuplicateGroup]) -> GroupAnalysisResult:
    """Analyze groups for patterns and insights."""
    result = GroupAnalysisResult()

    # Extension patterns
    ext_counts: dict[str, int] = {}
    for g in groups:
        if g.files:
            ext = g.files[0].ext.lower()
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    result.patterns.update(ext_counts)

    # Large group insights
    for g in groups:
        if g.count >= 10:
            result.insights.append(GroupInsight(
                group_id=g.group_id,
                insight_type="anomaly",
                title=f"Large group: {g.count} files",
                description=f"Group has {g.count} duplicates of {g.size_display} files",
                severity="warning",
            ))

    # High waste insights
    for g in groups:
        if g.wasted_space > 100_000_000:  # >100MB
            result.insights.append(GroupInsight(
                group_id=g.group_id,
                insight_type="optimization",
                title=f"High waste: {g.wasted_display}",
                description=f"Group wastes {g.wasted_display} with {g.count} copies",
                severity="warning",
            ))

    # Extension dominance
    if ext_counts:
        top_ext = max(ext_counts.items(), key=lambda x: x[1])
        if top_ext[1] > len(groups) * 0.5:
            result.insights.append(GroupInsight(
                group_id=-1,
                insight_type="pattern",
                title=f"Dominant extension: .{top_ext[0]}",
                description=(
                    f"{top_ext[1]} groups "
                    f"({top_ext[1] / len(groups) * 100:.0f}%) "
                    f"share the same extension"
                ),
                severity="info",
            ))

    return result


def format_group_insights(result: GroupAnalysisResult) -> str:
    """Format insights as text."""
    if not result.insights:
        return "No insights found."

    icons = {"info": "[i]", "warning": "[!]", "critical": "[X]"}
    lines = [f"Group Insights ({result.insight_count}):", ""]

    for insight in result.insights:
        icon = icons.get(insight.severity, "[?]")
        lines.append(f"  {icon} {insight.title}")
        lines.append(f"     {insight.description}")

    return "\n".join(lines)
