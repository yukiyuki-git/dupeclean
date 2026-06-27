"""File grouping module for DupeClean.

Group files by various criteria for batch operations.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class FileGroup:
    """A group of files."""

    key: str
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


def group_by_extension(
    files: list[FileInfo],
) -> list[FileGroup]:
    """Group files by extension."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)
    for fi in files:
        ext = fi.ext or "(none)"
        groups[ext].append(fi)
    result = [FileGroup(key=ext, files=group_files) for ext, group_files in groups.items()]
    result.sort(key=lambda g: g.total_size, reverse=True)
    return result


def group_by_size_range(
    files: list[FileInfo],
    ranges: list[tuple[str, int, int]] | None = None,
) -> list[FileGroup]:
    """Group files by size range."""
    if ranges is None:
        ranges = [
            ("empty", 0, 1),
            ("tiny", 1, 1024),
            ("small", 1024, 65536),
            ("medium", 65536, 1048576),
            ("large", 1048576, 104857600),
            ("huge", 104857600, 2**63),
        ]

    groups = {name: FileGroup(key=name) for name, _, _ in ranges}

    for fi in files:
        for name, min_s, max_s in ranges:
            if min_s <= fi.size < max_s:
                groups[name].files.append(fi)
                break

    return [g for g in groups.values() if g.files]


def group_by_directory(
    files: list[FileInfo],
) -> list[FileGroup]:
    """Group files by their parent directory."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)
    for fi in files:
        parent = str(fi.path.parent)
        groups[parent].append(fi)
    result = [
        FileGroup(key=dir_path, files=group_files) for dir_path, group_files in groups.items()
    ]
    result.sort(key=lambda g: g.total_size, reverse=True)
    return result


def group_by_age(
    files: list[FileInfo],
) -> list[FileGroup]:
    """Group files by age (modification time)."""
    import time

    now = time.time()
    age_ranges = [
        ("today", 0, 1),
        ("this_week", 1, 7),
        ("this_month", 7, 30),
        ("this_year", 30, 365),
        ("older", 365, 999999),
    ]

    groups = {name: FileGroup(key=name) for name, _, _ in age_ranges}

    for fi in files:
        age_days = (now - fi.mtime) / 86400 if fi.mtime > 0 else 999999
        for name, min_d, max_d in age_ranges:
            if min_d <= age_days < max_d:
                groups[name].files.append(fi)
                break

    return [g for g in groups.values() if g.files]


def format_groups(groups: list[FileGroup], title: str = "Groups") -> str:
    """Format file groups as text."""
    if not groups:
        return f"No {title.lower()} found."

    total = sum(g.count for g in groups)
    total_size = sum(g.total_size for g in groups)
    lines = [
        f"{title}: {len(groups)} groups, {total:,} files, {format_size(total_size)} total",
        "",
    ]

    for g in groups[:20]:
        pct = (g.total_size / total_size * 100) if total_size else 0
        lines.append(f"  {g.key:<20s} {g.count:>6,} files  {g.size_display:>10s} ({pct:5.1f}%)")

    if len(groups) > 20:
        lines.append(f"\n  ... and {len(groups) - 20} more groups")

    return "\n".join(lines)
