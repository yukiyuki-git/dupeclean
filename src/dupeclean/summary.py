"""File deduplication summary module for DupeClean.

Generate executive summaries of dedup analysis.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class DedupSummary:
    """Executive summary of dedup analysis."""

    total_files_scanned: int = 0
    total_size_scanned: int = 0
    duplicate_groups: int = 0
    duplicate_files: int = 0
    space_wasted: int = 0
    potential_savings: int = 0
    scan_duration: float = 0.0
    largest_dup_group: int = 0
    most_common_ext: str = ""

    @property
    def waste_percentage(self) -> float:
        if self.total_size_scanned == 0:
            return 0.0
        return (self.space_wasted / self.total_size_scanned) * 100

    @property
    def dupe_percentage(self) -> float:
        if self.total_files_scanned == 0:
            return 0.0
        return (self.duplicate_files / self.total_files_scanned) * 100


def create_summary(
    files: list[FileInfo],
    groups: list[DuplicateGroup],
    scan_duration: float = 0.0,
) -> DedupSummary:
    """Create executive summary from analysis results."""
    summary = DedupSummary(
        total_files_scanned=len(files),
        total_size_scanned=sum(f.size for f in files),
        duplicate_groups=len(groups),
        duplicate_files=sum(g.count for g in groups),
        space_wasted=sum(g.wasted_space for g in groups),
        scan_duration=scan_duration,
    )

    if groups:
        summary.largest_dup_group = max(g.count for g in groups)

    # Most common extension among duplicates
    ext_counts: dict[str, int] = {}
    for g in groups:
        for fi in g.files:
            ext = fi.ext or "(none)"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    if ext_counts:
        summary.most_common_ext = max(
            ext_counts,
            key=ext_counts.get,  # type: ignore
        )

    return summary


def format_summary(summary: DedupSummary) -> str:
    """Format executive summary as text."""
    lines = [
        "DupeClean Executive Summary",
        "=" * 30,
        "",
        f"Files scanned: {summary.total_files_scanned:,}",
        f"Total size: {format_size(summary.total_size_scanned)}",
        f"Scan time: {summary.scan_duration:.1f}s",
        "",
        f"Duplicate groups: {summary.duplicate_groups:,}",
        f"Duplicate files: {summary.duplicate_files:,} ({summary.dupe_percentage:.1f}%)",
        f"Space wasted: {format_size(summary.space_wasted)} ({summary.waste_percentage:.1f}%)",
    ]

    if summary.largest_dup_group > 0:
        lines.append(f"Largest dup group: {summary.largest_dup_group} files")
    if summary.most_common_ext:
        lines.append(f"Most common dup type: .{summary.most_common_ext}")

    return "\n".join(lines)


def format_brief_summary(summary: DedupSummary) -> str:
    """Format a brief one-line summary."""
    if summary.duplicate_groups == 0:
        return "No duplicates found."
    return (
        f"{summary.duplicate_groups:,} groups, "
        f"{summary.duplicate_files:,} files, "
        f"{format_size(summary.space_wasted)} wasted "
        f"({summary.waste_percentage:.1f}%)"
    )
