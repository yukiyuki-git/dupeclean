"""File age analysis module for DupeClean."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class AgeBucket:
    """Files grouped by age range."""

    label: str
    min_age_days: float
    max_age_days: float
    files: list[FileInfo] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)


# Age bucket definitions
AGE_BUCKETS = [
    ("Today", 0, 1),
    ("This week", 1, 7),
    ("This month", 7, 30),
    ("Last 3 months", 30, 90),
    ("Last 6 months", 90, 180),
    ("Last year", 180, 365),
    ("1-2 years", 365, 730),
    ("2+ years", 730, float("inf")),
]


def analyze_file_ages(
    files: list[FileInfo],
) -> list[AgeBucket]:
    """Group files by their age (modification time).

    Returns list of AgeBucket sorted from newest to oldest.
    """
    now = time.time()
    buckets = [
        AgeBucket(label=label, min_age_days=min_d, max_age_days=max_d)
        for label, min_d, max_d in AGE_BUCKETS
    ]

    for fi in files:
        age_seconds = now - fi.mtime
        age_days = age_seconds / 86400

        for bucket in buckets:
            if bucket.min_age_days <= age_days < bucket.max_age_days:
                bucket.files.append(fi)
                break

    return buckets


def get_oldest_files(files: list[FileInfo], n: int = 20) -> list[FileInfo]:
    """Get the N oldest files."""
    return sorted(files, key=lambda f: f.mtime)[:n]


def get_newest_files(files: list[FileInfo], n: int = 20) -> list[FileInfo]:
    """Get the N newest files."""
    return sorted(files, key=lambda f: f.mtime, reverse=True)[:n]


def format_age(seconds: float) -> str:
    """Format age in seconds to human-readable string."""
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    if seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    days = int(seconds / 86400)
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        months = days // 30
        return f"{months}mo ago"
    years = days // 365
    return f"{years}y ago"
