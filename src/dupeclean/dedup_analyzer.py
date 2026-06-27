"""File deduplication analyzer module for DupeClean.

High-level dedup analysis combining multiple techniques.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, ScanStats, format_size


@dataclass
class DedupAnalysis:
    """Complete dedup analysis result."""

    scan_stats: ScanStats
    exact_groups: list[DuplicateGroup] = field(default_factory=list)
    size_groups: list[DuplicateGroup] = field(default_factory=list)
    analysis_time: float = 0.0

    @property
    def total_duplicates(self) -> int:
        return sum(g.count for g in self.exact_groups)

    @property
    def total_wasted(self) -> int:
        return sum(g.wasted_space for g in self.exact_groups)

    @property
    def potential_savings(self) -> int:
        return self.total_wasted

    @property
    def savings_display(self) -> str:
        return format_size(self.potential_savings)


def analyze_dedup_potential(
    files: list[FileInfo],
    stats: ScanStats,
) -> DedupAnalysis:
    """Analyze dedup potential of a file set.

    Args:
        files: Files to analyze.
        stats: Scan statistics.

    Returns:
        DedupAnalysis with findings.
    """
    analysis = DedupAnalysis(scan_stats=stats)

    # Group by size
    size_groups: dict[int, list[FileInfo]] = {}
    for fi in files:
        if fi.size > 0:
            size_groups.setdefault(fi.size, []).append(fi)

    for size, group_files in size_groups.items():
        if len(group_files) >= 2:
            analysis.size_groups.append(
                DuplicateGroup(
                    group_id=len(analysis.size_groups),
                    hash_value=f"size_{size}",
                    file_size=size,
                    files=group_files,
                )
            )

    return analysis


def format_dedup_analysis(analysis: DedupAnalysis) -> str:
    """Format dedup analysis as text."""
    s = analysis.scan_stats
    lines = [
        "Dedup Analysis:",
        f"  Files: {s.total_files:,}",
        f"  Size: {format_size(s.total_size)}",
        f"  Size-based groups: {len(analysis.size_groups):,}",
        f"  Exact groups: {len(analysis.exact_groups):,}",
        f"  Potential savings: {analysis.savings_display}",
    ]
    return "\n".join(lines)
