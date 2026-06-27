"""Smart suggestions module for DupeClean.

Analyzes scan results and generates actionable recommendations:
- What to clean up first for maximum space savings
- Which directories are growing fastest
- Files that could be compressed
- Duplicate clusters worth consolidating
- Old files that could be archived
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .analyzer import AnalysisResult
from .models import FileInfo, format_size


@dataclass
class Suggestion:
    """A cleanup or optimization suggestion."""

    priority: int  # 1 = highest, 5 = lowest
    category: str  # "cleanup", "compress", "archive", "organize"
    title: str
    description: str
    estimated_savings: int = 0
    files: list[FileInfo] = field(default_factory=list)

    @property
    def savings_display(self) -> str:
        return format_size(self.estimated_savings)


def generate_suggestions(
    result: AnalysisResult,
) -> list[Suggestion]:
    """Generate smart suggestions from analysis results.

    Returns list of Suggestion sorted by priority (highest first).
    """
    suggestions: list[Suggestion] = []

    # 1. Duplicate cleanup (highest priority)
    if result.duplicates:
        suggestions.append(_suggest_duplicate_cleanup(result))

    # 2. Large files review
    large_suggestion = _suggest_large_files(result)
    if large_suggestion:
        suggestions.append(large_suggestion)

    # 3. Old files archive
    old_suggestion = _suggest_old_files(result)
    if old_suggestion:
        suggestions.append(old_suggestion)

    # 4. Compressible files
    compress_suggestion = _suggest_compression(result)
    if compress_suggestion:
        suggestions.append(compress_suggestion)

    # 5. Empty files cleanup
    empty_suggestion = _suggest_empty_cleanup(result)
    if empty_suggestion:
        suggestions.append(empty_suggestion)

    # Sort by priority
    suggestions.sort(key=lambda s: s.priority)
    return suggestions


def _suggest_duplicate_cleanup(
    result: AnalysisResult,
) -> Suggestion:
    total_wasted = sum(g.wasted_space for g in result.duplicates)
    dup_files = [f for g in result.duplicates for f in g.files[1:]]
    return Suggestion(
        priority=1,
        category="cleanup",
        title="Remove duplicate files",
        description=(
            f"Found {len(result.duplicates)} duplicate groups "
            f"wasting {format_size(total_wasted)}. "
            f"Run dupeclean --duplicates to review."
        ),
        estimated_savings=total_wasted,
        files=dup_files[:50],
    )


def _suggest_large_files(
    result: AnalysisResult,
) -> Suggestion | None:
    large = [f for f in result.largest_files if f.size > 100_000_000]
    if not large:
        return None
    total = sum(f.size for f in large)
    return Suggestion(
        priority=2,
        category="cleanup",
        title=f"Review {len(large)} large files (>100MB)",
        description=(
            f"Found {len(large)} files over 100MB totaling "
            f"{format_size(total)}. Consider moving to "
            f"external storage."
        ),
        estimated_savings=total,
        files=large,
    )


def _suggest_old_files(
    result: AnalysisResult,
) -> Suggestion | None:
    import time

    now = time.time()
    year_ago = now - (365 * 86400)
    old_files = [f for f in result.files if f.mtime < year_ago]
    if len(old_files) < 10:
        return None
    total = sum(f.size for f in old_files)
    return Suggestion(
        priority=3,
        category="archive",
        title=f"Archive {len(old_files)} old files (>1 year)",
        description=(
            f"Found {len(old_files)} files not modified in "
            f"over a year ({format_size(total)}). "
            f"Consider archiving to free space."
        ),
        estimated_savings=total,
        files=old_files[:50],
    )


def _suggest_compression(
    result: AnalysisResult,
) -> Suggestion | None:
    compressible_exts = {
        ".txt",
        ".log",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".js",
        ".py",
        ".md",
        ".yaml",
    }
    compressible = [f for f in result.files if f.ext in compressible_exts and f.size > 10000]
    if not compressible:
        return None
    total = sum(f.size for f in compressible)
    estimated_savings = int(total * 0.6)
    return Suggestion(
        priority=4,
        category="compress",
        title=f"Compress {len(compressible)} text files",
        description=(
            f"Found {len(compressible)} compressible text files "
            f"({format_size(total)}). Estimated savings: "
            f"{format_size(estimated_savings)}."
        ),
        estimated_savings=estimated_savings,
        files=compressible[:50],
    )


def _suggest_empty_cleanup(
    result: AnalysisResult,
) -> Suggestion | None:
    empty = [f for f in result.files if f.size == 0]
    if not empty:
        return None
    return Suggestion(
        priority=5,
        category="cleanup",
        title=f"Remove {len(empty)} empty files",
        description=(f"Found {len(empty)} empty files that can safely be removed."),
        estimated_savings=0,
        files=empty[:50],
    )


def format_suggestions(
    suggestions: list[Suggestion],
) -> str:
    """Format suggestions as human-readable text."""
    if not suggestions:
        return "No suggestions — your disk looks clean!"

    lines = ["Smart Suggestions:", ""]
    for i, s in enumerate(suggestions, 1):
        priority_icon = "🔴" if s.priority <= 2 else "🟡" if s.priority <= 4 else "🟢"
        lines.append(f"  {priority_icon} {i}. [{s.category.upper()}] {s.title}")
        lines.append(f"     {s.description}")
        if s.estimated_savings > 0:
            lines.append(f"     Estimated savings: {s.savings_display}")
        lines.append("")

    total_savings = sum(s.estimated_savings for s in suggestions)
    if total_savings > 0:
        lines.append(f"  Total potential savings: {format_size(total_savings)}")

    return "\n".join(lines)
