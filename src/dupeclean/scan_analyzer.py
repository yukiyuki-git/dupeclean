"""File deduplication scan result analyzer for DupeClean.

Analyze scan results for insights and patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, ScanStats, format_size


@dataclass
class ScanInsight:
    """An insight from scan analysis."""

    category: str  # "size", "type", "age", "duplicate"
    title: str
    description: str
    severity: str = "info"  # "info", "warning", "critical"

    @property
    def icon(self) -> str:
        icons = {"info": "[i]", "warning": "[!]", "critical": "[X]"}
        return icons.get(self.severity, "[?]")


@dataclass
class ScanAnalysisResult:
    """Result of scan analysis."""

    insights: list[ScanInsight] = field(default_factory=list)
    stats: ScanStats | None = None

    @property
    def insight_count(self) -> int:
        return len(self.insights)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity in ("warning", "critical") for i in self.insights)


def analyze_scan_result(
    files: list[FileInfo],
    stats: ScanStats,
) -> ScanAnalysisResult:
    """Analyze scan results for insights."""
    result = ScanAnalysisResult(stats=stats)

    # Check for very large files
    large = [f for f in files if f.size > 1_000_000_000]
    if large:
        result.insights.append(
            ScanInsight(
                category="size",
                title=f"{len(large)} very large files (>1GB)",
                description=f"Total: {format_size(sum(f.size for f in large))}",
                severity="warning",
            )
        )

    # Check for many small files
    small = [f for f in files if f.size < 100]
    if len(small) > 1000:
        result.insights.append(
            ScanInsight(
                category="size",
                title=f"{len(small):,} very small files (<100B)",
                description="Consider consolidating small files",
                severity="info",
            )
        )

    # Check for old files
    import time

    year_ago = time.time() - (365 * 86400)
    old = [f for f in files if f.mtime < year_ago]
    if old:
        result.insights.append(
            ScanInsight(
                category="age",
                title=f"{len(old):,} files older than 1 year",
                description=f"Total: {format_size(sum(f.size for f in old))}",
                severity="info",
            )
        )

    # Check for temp files
    temp_exts = {".tmp", ".temp", ".bak", ".log"}
    temp = [f for f in files if f.ext.lower() in temp_exts]
    if temp:
        result.insights.append(
            ScanInsight(
                category="cleanup",
                title=f"{len(temp)} temp/log files",
                description=f"Total: {format_size(sum(f.size for f in temp))}",
                severity="info",
            )
        )

    return result


def format_scan_insights(result: ScanAnalysisResult) -> str:
    """Format scan insights as text."""
    if not result.insights:
        return "No insights found."

    lines = [f"Scan Insights ({result.insight_count}):", ""]
    for insight in result.insights:
        icon = insight.icon
        lines.append(f"  {icon} {insight.title}")
        lines.append(f"     {insight.description}")

    return "\n".join(lines)
