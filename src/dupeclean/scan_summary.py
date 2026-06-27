"""File deduplication scan summary module for DupeClean.

Generate executive summaries of scan results.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import ScanStats, format_duration, format_size


@dataclass
class ScanSummary:
    """Executive summary of a scan."""

    total_files: int = 0
    total_dirs: int = 0
    total_size: int = 0
    scan_duration: float = 0.0
    duplicate_groups: int = 0
    duplicate_files: int = 0
    wasted_space: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)

    @property
    def wasted_display(self) -> str:
        return format_size(self.wasted_space)

    @property
    def dupe_pct(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.duplicate_files / self.total_files) * 100

    @property
    def waste_pct(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.wasted_space / self.total_size) * 100


def create_scan_summary(stats: ScanStats) -> ScanSummary:
    """Create summary from scan statistics."""
    return ScanSummary(
        total_files=stats.total_files,
        total_dirs=stats.total_dirs,
        total_size=stats.total_size,
        scan_duration=stats.scan_duration,
        duplicate_groups=stats.duplicate_groups,
        duplicate_files=stats.duplicate_files,
        wasted_space=stats.wasted_space,
    )


def format_scan_summary(summary: ScanSummary) -> str:
    """Format scan summary as text."""
    lines = [
        "Scan Summary",
        "=" * 12,
        f"  Files: {summary.total_files:,}",
        f"  Dirs: {summary.total_dirs:,}",
        f"  Size: {summary.size_display}",
        f"  Duration: {format_duration(summary.scan_duration)}",
    ]

    if summary.duplicate_groups > 0:
        lines.extend(
            [
                "",
                f"  Duplicate groups: {summary.duplicate_groups:,}",
                f"  Duplicate files: {summary.duplicate_files:,} ({summary.dupe_pct:.1f}%)",
                f"  Wasted: {summary.wasted_display} ({summary.waste_pct:.1f}%)",
            ]
        )

    return "\n".join(lines)


def format_brief_summary(summary: ScanSummary) -> str:
    """Format a one-line summary."""
    parts = [
        f"{summary.total_files:,} files",
        summary.size_display,
    ]
    if summary.duplicate_groups > 0:
        parts.append(f"{summary.duplicate_groups} dupe groups, {summary.wasted_display} wasted")
    return " | ".join(parts)
