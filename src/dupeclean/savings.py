"""File deduplication space savings calculator for DupeClean.

Calculate potential and actual space savings from dedup.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DuplicateGroup, format_size


@dataclass
class SavingsBreakdown:
    """Breakdown of space savings."""

    total_savings: int = 0
    by_size: dict[str, int] = None  # size range -> savings
    by_extension: dict[str, int] = None  # ext -> savings

    def __post_init__(self) -> None:
        if self.by_size is None:
            self.by_size = {}
        if self.by_extension is None:
            self.by_extension = {}

    @property
    def savings_display(self) -> str:
        return format_size(self.total_savings)


def calculate_savings(groups: list[DuplicateGroup]) -> SavingsBreakdown:
    """Calculate savings from duplicate groups."""
    breakdown = SavingsBreakdown()

    for group in groups:
        savings = group.wasted_space
        breakdown.total_savings += savings

        # By size range
        size_range = _get_size_range(group.file_size)
        breakdown.by_size[size_range] = breakdown.by_size.get(size_range, 0) + savings

        # By extension
        if group.files:
            ext = group.files[0].ext or "(none)"
            breakdown.by_extension[ext] = breakdown.by_extension.get(ext, 0) + savings

    return breakdown


def _get_size_range(size: int) -> str:
    """Get human-readable size range."""
    if size < 1024:
        return "<1KB"
    if size < 65536:
        return "1-64KB"
    if size < 1048576:
        return "64KB-1MB"
    if size < 16777216:
        return "1-16MB"
    return ">16MB"


def calculate_actual_savings(
    files_before: int,
    size_before: int,
    files_after: int,
    size_after: int,
) -> dict:
    """Calculate actual savings from a cleanup operation."""
    return {
        "files_removed": files_before - files_after,
        "space_freed": size_before - size_after,
        "space_freed_display": format_size(size_before - size_after),
        "reduction_pct": (
            ((size_before - size_after) / size_before * 100) if size_before > 0 else 0
        ),
    }


def format_savings(breakdown: SavingsBreakdown) -> str:
    """Format savings breakdown as text."""
    lines = [
        f"Space Savings: {breakdown.savings_display}",
        "",
        "By size range:",
    ]

    for size_range, savings in sorted(breakdown.by_size.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {size_range:<12s} {format_size(savings):>10s}")

    if breakdown.by_extension:
        lines.append("\nBy extension:")
        sorted_exts = sorted(breakdown.by_extension.items(), key=lambda x: x[1], reverse=True)
        for ext, savings in sorted_exts[:10]:
            lines.append(f"  .{ext:<12s} {format_size(savings):>10s}")

    return "\n".join(lines)
