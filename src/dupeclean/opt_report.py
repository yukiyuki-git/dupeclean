"""File deduplication optimization report for DupeClean.

Generate optimization reports with actionable recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class Recommendation:
    """An optimization recommendation."""

    priority: int  # 1 = highest
    category: str
    title: str
    description: str
    estimated_savings: int = 0

    @property
    def savings_display(self) -> str:
        return format_size(self.estimated_savings)


@dataclass
class OptimizationReport:
    """Complete optimization report."""

    recommendations: list[Recommendation] = field(default_factory=list)

    def add(self, rec: Recommendation) -> None:
        self.recommendations.append(rec)
        self.recommendations.sort(key=lambda r: r.priority)

    @property
    def total_savings(self) -> int:
        return sum(r.estimated_savings for r in self.recommendations)

    def render(self) -> str:
        """Render report as text."""
        if not self.recommendations:
            return "No optimization recommendations."

        lines = [
            f"Optimization Report: {len(self.recommendations)} recommendations",
            f"Total potential savings: {format_size(self.total_savings)}",
            "",
        ]

        for i, rec in enumerate(self.recommendations, 1):
            icon = "🔴" if rec.priority <= 2 else "🟡" if rec.priority <= 4 else "🟢"
            lines.append(f"  {icon} {i}. [{rec.category}] {rec.title}")
            lines.append(f"     {rec.description}")
            if rec.estimated_savings > 0:
                lines.append(f"     Savings: {rec.savings_display}")
            lines.append("")

        return "\n".join(lines)


def generate_report(
    files: list[FileInfo],
    groups: list[DuplicateGroup],
) -> OptimizationReport:
    """Generate optimization report from analysis."""
    report = OptimizationReport()

    # Duplicate cleanup
    if groups:
        wasted = sum(g.wasted_space for g in groups)
        report.add(
            Recommendation(
                priority=1,
                category="dedup",
                title="Remove duplicate files",
                description=f"{len(groups)} groups wasting {format_size(wasted)}",
                estimated_savings=wasted,
            )
        )

    # Large files
    large = [f for f in files if f.size > 100_000_000]
    if large:
        total = sum(f.size for f in large)
        report.add(
            Recommendation(
                priority=2,
                category="storage",
                title=f"Review {len(large)} large files (>100MB)",
                description=f"Total: {format_size(total)}",
                estimated_savings=total // 2,
            )
        )

    # Temporary files
    temp_exts = {".tmp", ".temp", ".bak", ".log"}
    temp_files = [f for f in files if f.ext.lower() in temp_exts]
    if temp_files:
        total = sum(f.size for f in temp_files)
        report.add(
            Recommendation(
                priority=3,
                category="cleanup",
                title=f"Clean {len(temp_files)} temp/log files",
                description=f"Total: {format_size(total)}",
                estimated_savings=total,
            )
        )

    return report
