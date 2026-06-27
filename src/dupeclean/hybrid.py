"""File deduplication engine v3 for DupeClean.

Hybrid dedup combining multiple detection methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class HybridDedupResult:
    """Result of hybrid deduplication analysis."""

    exact_duplicates: list[DuplicateGroup] = field(default_factory=list)
    similar_names: list[DuplicateGroup] = field(default_factory=list)
    total_savings: int = 0
    method_stats: dict[str, int] = field(default_factory=dict)

    @property
    def total_groups(self) -> int:
        return len(self.exact_duplicates) + len(self.similar_names)

    @property
    def savings_display(self) -> str:
        return format_size(self.total_savings)


def analyze_hybrid(
    files: list[FileInfo],
    groups: list[DuplicateGroup],
) -> HybridDedupResult:
    """Run hybrid dedup analysis combining multiple methods.

    Args:
        files: All files from scan.
        groups: Exact duplicate groups from primary dedup.

    Returns:
        HybridDedupResult with combined findings.
    """
    result = HybridDedupResult()

    # Method 1: Exact duplicates (from primary dedup)
    result.exact_duplicates = groups
    result.method_stats["exact"] = len(groups)
    result.total_savings += sum(g.wasted_space for g in groups)

    # Method 2: Similar names (same extension, similar stem)
    similar = _find_similar_names(files)
    result.similar_names = similar
    result.method_stats["similar_names"] = len(similar)
    result.total_savings += sum(g.wasted_space for g in similar)

    return result


def _find_similar_names(
    files: list[FileInfo],
) -> list[DuplicateGroup]:
    """Find files with very similar names."""
    from .fuzzy import find_similar_names

    fuzzy_groups = find_similar_names(files, threshold=0.85)

    # Convert to DuplicateGroup format
    result: list[DuplicateGroup] = []
    for i, fg in enumerate(fuzzy_groups):
        if fg.count >= 2:
            result.append(
                DuplicateGroup(
                    group_id=1000 + i,
                    hash_value=f"similar_{i}",
                    file_size=fg.files[0].size,
                    files=fg.files,
                )
            )

    return result


def format_hybrid_result(result: HybridDedupResult) -> str:
    """Format hybrid dedup results as text."""
    lines = [
        "Hybrid Dedup Analysis:",
        f"  Total groups: {result.total_groups}",
        f"  Total savings: {result.savings_display}",
        "",
        "  By method:",
    ]

    for method, count in result.method_stats.items():
        lines.append(f"    {method}: {count} groups")

    if result.exact_duplicates:
        lines.append("\n  Top exact duplicates:")
        for g in result.exact_duplicates[:5]:
            lines.append(
                f"    Group #{g.group_id}: {g.count} x {g.size_display} = {g.wasted_display} wasted"
            )

    return "\n".join(lines)
