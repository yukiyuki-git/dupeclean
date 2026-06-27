"""File scoring module for DupeClean.

Score files based on multiple criteria for prioritization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class ScoreComponent:
    """A single scoring component."""

    name: str
    weight: float
    value: float  # 0.0 to 1.0

    @property
    def weighted(self) -> float:
        return self.weight * self.value


@dataclass
class FileScore:
    """Composite score for a file."""

    file: FileInfo
    components: list[ScoreComponent] = field(default_factory=list)

    @property
    def total(self) -> float:
        if not self.components:
            return 0.0
        return sum(c.weighted for c in self.components)

    @property
    def max_possible(self) -> float:
        return sum(c.weight for c in self.components)


def score_by_size(fi: FileInfo, max_size: int) -> ScoreComponent:
    """Score by file size (larger = higher score)."""
    value = min(1.0, fi.size / max_size) if max_size > 0 else 0
    return ScoreComponent(name="size", weight=0.3, value=value)


def score_by_age(fi: FileInfo, max_age_days: float = 365) -> ScoreComponent:
    """Score by age (older = higher score)."""
    age_days = (time.time() - fi.mtime) / 86400 if fi.mtime > 0 else max_age_days
    value = min(1.0, age_days / max_age_days)
    return ScoreComponent(name="age", weight=0.2, value=value)


def score_by_extension(
    fi: FileInfo,
    priority_exts: set[str] | None = None,
) -> ScoreComponent:
    """Score by extension priority."""
    if priority_exts is None:
        priority_exts = {".tmp", ".log", ".bak", ".cache"}
    value = 1.0 if fi.ext.lower() in priority_exts else 0.0
    return ScoreComponent(name="extension", weight=0.2, value=value)


def score_by_path_depth(fi: FileInfo) -> ScoreComponent:
    """Score by path depth (deeper = higher score)."""
    depth = len(fi.path.parts)
    value = min(1.0, depth / 10)
    return ScoreComponent(name="depth", weight=0.1, value=value)


def score_by_duplicates(fi: FileInfo, is_duplicate: bool) -> ScoreComponent:
    """Score by duplicate status."""
    value = 1.0 if is_duplicate else 0.0
    return ScoreComponent(name="duplicate", weight=0.2, value=value)


def compute_file_score(
    fi: FileInfo,
    max_size: int = 1073741824,
    max_age_days: float = 365,
    priority_exts: set[str] | None = None,
    is_duplicate: bool = False,
) -> FileScore:
    """Compute composite score for a file."""
    return FileScore(
        file=fi,
        components=[
            score_by_size(fi, max_size),
            score_by_age(fi, max_age_days),
            score_by_extension(fi, priority_exts),
            score_by_path_depth(fi),
            score_by_duplicates(fi, is_duplicate),
        ],
    )


def score_files(
    files: list[FileInfo],
    max_size: int = 1073741824,
    duplicate_set: set[Path] | None = None,
) -> list[FileScore]:
    """Score all files and return sorted by score descending."""
    dup_set = duplicate_set or set()
    scores = []
    for fi in files:
        score = compute_file_score(
            fi,
            max_size=max_size,
            is_duplicate=fi.path in dup_set,
        )
        scores.append(score)
    scores.sort(key=lambda s: s.total, reverse=True)
    return scores


def format_file_scores(scores: list[FileScore], count: int = 20) -> str:
    """Format file scores as text."""
    if not scores:
        return "No files to score."

    lines = [
        f"File Scores (top {min(count, len(scores))} of {len(scores):,}):",
        "",
    ]

    for s in scores[:count]:
        components = " ".join(f"{c.name}={c.value:.1f}" for c in s.components)
        lines.append(
            f"  {s.total:5.2f}  {s.file.size_display:>10s}  {s.file.path.name}  [{components}]"
        )

    return "\n".join(lines)
