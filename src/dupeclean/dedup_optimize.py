"""File deduplication optimization strategies for DupeClean.

Optimize dedup operations based on file characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import FileInfo, format_size


@dataclass
class OptimizationSuggestion:
    """A suggestion for optimizing dedup."""

    name: str
    description: str
    estimated_speedup: float = 1.0
    estimated_savings: int = 0
    priority: int = 0


def suggest_optimizations(
    files: list[FileInfo],
) -> list[OptimizationSuggestion]:
    """Suggest optimizations based on file characteristics."""
    suggestions: list[OptimizationSuggestion] = []

    # Check for many small files
    small_files = [f for f in files if f.size < 4096]
    if len(small_files) > 1000:
        suggestions.append(
            OptimizationSuggestion(
                name="batch_small_files",
                description=(
                    f"{len(small_files):,} small files detected. Batch processing recommended."
                ),
                estimated_speedup=2.0,
                priority=1,
            )
        )

    # Check for many unique sizes
    sizes = set(f.size for f in files)
    unique_ratio = len(sizes) / len(files) if files else 0
    if unique_ratio > 0.9:
        suggestions.append(
            OptimizationSuggestion(
                name="skip_hashing",
                description=("90%+ files have unique sizes. Size-based filtering sufficient."),
                estimated_speedup=10.0,
                priority=2,
            )
        )

    # Check for large files
    large_files = [f for f in files if f.size > 100_000_000]
    if large_files:
        total = sum(f.size for f in large_files)
        suggestions.append(
            OptimizationSuggestion(
                name="parallel_large_files",
                description=(
                    f"{len(large_files)} large files "
                    f"({format_size(total)}). "
                    f"Parallel hashing recommended."
                ),
                estimated_speedup=4.0,
                priority=3,
            )
        )

    # Check for many files with same extension
    ext_counts: dict[str, int] = {}
    for fi in files:
        ext = fi.ext or "(none)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    top_ext = max(ext_counts.items(), key=lambda x: x[1], default=("", 0))
    if top_ext[1] > len(files) * 0.5:
        suggestions.append(
            OptimizationSuggestion(
                name="group_by_extension",
                description=(
                    f".{top_ext[0]} dominates "
                    f"({top_ext[1]:,} files, "
                    f"{top_ext[1] / len(files) * 100:.0f}%). "
                    f"Group by extension first."
                ),
                estimated_speedup=1.5,
                priority=4,
            )
        )

    suggestions.sort(key=lambda s: s.priority)
    return suggestions


def format_suggestions(
    suggestions: list[OptimizationSuggestion],
) -> str:
    """Format optimization suggestions as text."""
    if not suggestions:
        return "No optimization suggestions."

    lines = [
        f"Optimization Suggestions ({len(suggestions)}):",
        "",
    ]

    for s in suggestions:
        lines.append(f"  {s.name} (speedup: {s.estimated_speedup:.1f}x)")
        lines.append(f"    {s.description}")

    return "\n".join(lines)
