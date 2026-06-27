"""File optimization module for DupeClean.

Suggest optimizations for file storage:
- Compression candidates
- Deduplication candidates
- Archival candidates
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class Optimization:
    """A file optimization suggestion."""

    file: FileInfo
    action: str  # "compress", "archive", "dedup", "delete"
    reason: str
    estimated_savings: int = 0

    @property
    def savings_display(self) -> str:
        return format_size(self.estimated_savings)


@dataclass
class OptimizationPlan:
    """Collection of optimization suggestions."""

    optimizations: list[Optimization] = field(default_factory=list)

    @property
    def total_savings(self) -> int:
        return sum(o.estimated_savings for o in self.optimizations)

    @property
    def count(self) -> int:
        return len(self.optimizations)


# File types that compress well
COMPRESSIBLE = {
    ".txt",
    ".log",
    ".csv",
    ".json",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".md",
    ".rst",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".sql",
    ".sh",
    ".bat",
    ".ps1",
    ".rb",
    ".go",
    ".rs",
}

# File types already compressed
ALREADY_COMPRESSED = {
    ".zip",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".mp3",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".flac",
    ".ogg",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".epub",
}

# Temporary file patterns
TEMP_EXTENSIONS = {
    ".tmp",
    ".temp",
    ".bak",
    ".swp",
    ".swo",
    ".orig",
    ".old",
    ".cache",
}


def find_compression_candidates(
    files: list[FileInfo],
    min_size: int = 10000,
) -> list[Optimization]:
    """Find files that would benefit from compression."""
    results = []
    for fi in files:
        ext = fi.ext.lower()
        if ext in COMPRESSIBLE and fi.size >= min_size:
            estimated = int(fi.size * 0.6)  # ~60% compression
            results.append(
                Optimization(
                    file=fi,
                    action="compress",
                    reason=f"Text file ({ext})",
                    estimated_savings=estimated,
                )
            )
    results.sort(key=lambda o: o.estimated_savings, reverse=True)
    return results


def find_archive_candidates(
    files: list[FileInfo],
    max_age_days: float = 365,
) -> list[Optimization]:
    """Find files that could be archived."""
    import time

    cutoff = time.time() - (max_age_days * 86400)
    results = []
    for fi in files:
        if fi.mtime < cutoff and fi.size > 0:
            results.append(
                Optimization(
                    file=fi,
                    action="archive",
                    reason=f"Not modified in {max_age_days:.0f} days",
                    estimated_savings=fi.size,
                )
            )
    results.sort(key=lambda o: o.file.size, reverse=True)
    return results


def find_temp_files(
    files: list[FileInfo],
) -> list[Optimization]:
    """Find temporary files that can be deleted."""
    results = []
    for fi in files:
        ext = fi.ext.lower()
        if ext in TEMP_EXTENSIONS:
            results.append(
                Optimization(
                    file=fi,
                    action="delete",
                    reason=f"Temporary file ({ext})",
                    estimated_savings=fi.size,
                )
            )
    return results


def create_optimization_plan(
    files: list[FileInfo],
) -> OptimizationPlan:
    """Create a complete optimization plan."""
    plan = OptimizationPlan()
    plan.optimizations.extend(find_compression_candidates(files))
    plan.optimizations.extend(find_archive_candidates(files))
    plan.optimizations.extend(find_temp_files(files))
    plan.optimizations.sort(key=lambda o: o.estimated_savings, reverse=True)
    return plan


def format_optimization_plan(plan: OptimizationPlan) -> str:
    """Format optimization plan as text."""
    if not plan.optimizations:
        return "No optimizations found."

    lines = [
        f"Optimization Plan: {plan.count} suggestions",
        f"Total potential savings: {format_size(plan.total_savings)}",
        "",
    ]

    by_action: dict[str, list[Optimization]] = {}
    for opt in plan.optimizations:
        by_action.setdefault(opt.action, []).append(opt)

    for action, opts in by_action.items():
        action_savings = sum(o.estimated_savings for o in opts)
        lines.append(
            f"  [{action.upper()}] {len(opts)} files, {format_size(action_savings)} savings"
        )
        for opt in opts[:5]:
            lines.append(f"    {opt.file.size_display:>10s}  {opt.file.path.name}  [{opt.reason}]")
        if len(opts) > 5:
            lines.append(f"    ... and {len(opts) - 5} more")
        lines.append("")

    return "\n".join(lines)
