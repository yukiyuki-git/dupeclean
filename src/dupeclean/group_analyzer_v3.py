"""File deduplication group analyzer v3 for DupeClean.

Advanced group analysis with ML-like pattern detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class Pattern:
    """A detected pattern."""
    pattern_type: str
    description: str
    frequency: int = 0
    impact: int = 0

    @property
    def impact_display(self) -> str:
        return format_size(self.impact)


@dataclass
class AnalysisV3Result:
    """Advanced analysis result."""
    patterns: list[Pattern] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def pattern_count(self) -> int:
        return len(self.patterns)

    @property
    def recommendation_count(self) -> int:
        return len(self.recommendations)


def analyze_advanced(groups: list[DuplicateGroup]) -> AnalysisV3Result:
    """Perform advanced analysis on duplicate groups."""
    result = AnalysisV3Result()

    if not groups:
        return result

    # Extension clustering
    ext_groups: dict[str, list[DuplicateGroup]] = {}
    for g in groups:
        ext = g.files[0].ext if g.files else ""
        ext_groups.setdefault(ext, []).append(g)

    for ext, ext_gs in ext_groups.items():
        if len(ext_gs) >= 3:
            total_waste = sum(g.wasted_space for g in ext_gs)
            result.patterns.append(Pattern(
                pattern_type="extension_cluster",
                description=f"Large cluster of .{ext} duplicates",
                frequency=len(ext_gs),
                impact=total_waste,
            ))

    # Size anomalies
    sizes = [g.file_size for g in groups]
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        for g in groups:
            if g.file_size > avg_size * 10:
                result.patterns.append(Pattern(
                    pattern_type="size_anomaly",
                    description=(
                        f"Group #{g.group_id} files are "
                        f"{g.file_size / avg_size:.0f}x larger than average"
                    ),
                    frequency=1,
                    impact=g.wasted_space,
                ))

    # High-dup groups
    for g in groups:
        if g.count >= 5:
            result.patterns.append(Pattern(
                pattern_type="high_duplication",
                description=f"Group #{g.group_id} has {g.count} duplicates",
                frequency=g.count,
                impact=g.wasted_space,
            ))

    # Generate recommendations
    total_waste = sum(g.wasted_space for g in groups)
    if total_waste > 1_000_000_000:
        result.recommendations.append("Large amount of wasted space - prioritize cleanup")
    if len(groups) > 100:
        result.recommendations.append("Many duplicate groups - consider batch cleanup")

    return result


def format_analysis_v3(result: AnalysisV3Result) -> str:
    """Format analysis as text."""
    lines = [
        f"Advanced Analysis: {result.pattern_count} patterns, "
        f"{result.recommendation_count} recommendations",
        "",
    ]

    for pattern in result.patterns[:10]:
        lines.append(f"  [{pattern.pattern_type}] {pattern.description}")
        lines.append(f"    Impact: {pattern.impact_display}, Frequency: {pattern.frequency}")

    if result.recommendations:
        lines.append("\n  Recommendations:")
        for rec in result.recommendations:
            lines.append(f"    - {rec}")

    return "\n".join(lines)
