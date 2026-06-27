"""File deduplication analyzer v2 for DupeClean.

Enhanced dedup analysis with multiple detection methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class AnalysisV2Result:
    """Enhanced analysis result."""

    total_files: int = 0
    total_size: int = 0
    size_groups: int = 0
    hash_groups: int = 0
    name_groups: int = 0
    total_duplicates: int = 0
    total_wasted: int = 0
    methods_used: list[str] = field(default_factory=list)

    @property
    def waste_pct(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.total_wasted / self.total_size) * 100

    @property
    def dupe_pct(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.total_duplicates / self.total_files) * 100


def analyze_v2(
    files: list[FileInfo],
    groups: list[DuplicateGroup],
) -> AnalysisV2Result:
    """Run enhanced dedup analysis."""
    result = AnalysisV2Result(
        total_files=len(files),
        total_size=sum(f.size for f in files),
    )

    # Size groups
    size_map: dict[int, list[FileInfo]] = {}
    for fi in files:
        if fi.size > 0:
            size_map.setdefault(fi.size, []).append(fi)
    result.size_groups = sum(1 for g in size_map.values() if len(g) >= 2)
    result.methods_used.append("size")

    # Hash groups from existing groups
    result.hash_groups = len(groups)
    result.total_duplicates = sum(g.count for g in groups)
    result.total_wasted = sum(g.wasted_space for g in groups)
    if groups:
        result.methods_used.append("hash")

    return result


def format_analysis_v2(result: AnalysisV2Result) -> str:
    """Format v2 analysis as text."""
    lines = [
        "Enhanced Analysis:",
        f"  Files: {result.total_files:,}",
        f"  Size: {format_size(result.total_size)}",
        f"  Size groups: {result.size_groups:,}",
        f"  Hash groups: {result.hash_groups:,}",
        f"  Total duplicates: {result.total_duplicates:,}",
        f"  Wasted: {format_size(result.total_wasted)} ({result.waste_pct:.1f}%)",
        f"  Dupe %: {result.dupe_pct:.1f}%",
        f"  Methods: {', '.join(result.methods_used)}",
    ]
    return "\n".join(lines)
