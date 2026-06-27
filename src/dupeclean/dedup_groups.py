"""File deduplication grouping module for DupeClean.

Group files by various dedup-relevant criteria.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class DedupGroup:
    """A group of potentially duplicate files."""

    key: str
    method: str  # "size", "name", "hash"
    files: list[FileInfo] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def file_size(self) -> int:
        return self.files[0].size if self.files else 0

    @property
    def wasted_space(self) -> int:
        return self.file_size * (self.count - 1)

    @property
    def wasted_display(self) -> str:
        return format_size(self.wasted_space)


def group_by_size(files: list[FileInfo]) -> list[DedupGroup]:
    """Group files by size (potential duplicates)."""
    groups: dict[int, list[FileInfo]] = defaultdict(list)
    for fi in files:
        if fi.size > 0:
            groups[fi.size].append(fi)
    result = []
    for size, group_files in groups.items():
        if len(group_files) >= 2:
            result.append(
                DedupGroup(
                    key=str(size),
                    method="size",
                    files=group_files,
                )
            )
    result.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def group_by_hash(
    files: list[FileInfo],
) -> list[DedupGroup]:
    """Group files by their hash (confirmed duplicates)."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)
    for fi in files:
        h = fi.hash_for_dedup
        if h:
            groups[h].append(fi)
    result = []
    for hash_val, group_files in groups.items():
        if len(group_files) >= 2:
            result.append(
                DedupGroup(
                    key=hash_val,
                    method="hash",
                    files=group_files,
                )
            )
    result.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def group_by_name_pattern(
    files: list[FileInfo],
) -> list[DedupGroup]:
    """Group files by normalized name (similar names)."""
    import re

    groups: dict[str, list[FileInfo]] = defaultdict(list)
    copy_pattern = re.compile(
        r"\s*\(?\d+\)?\s*$|\s*copy\s*$|\s*副本\s*$",
        re.IGNORECASE,
    )

    for fi in files:
        stem = fi.path.stem
        normalized = copy_pattern.sub("", stem).strip().lower()
        ext = fi.ext.lower()
        key = f"{normalized}.{ext}"
        if normalized:
            groups[key].append(fi)

    result = []
    for key, group_files in groups.items():
        if len(group_files) >= 2:
            result.append(
                DedupGroup(
                    key=key,
                    method="name",
                    files=group_files,
                )
            )
    result.sort(key=lambda g: g.count, reverse=True)
    return result


def format_dedup_groups(groups: list[DedupGroup]) -> str:
    """Format dedup groups as text."""
    if not groups:
        return "No duplicate groups found."

    total_wasted = sum(g.wasted_space for g in groups)
    lines = [
        f"Dedup Groups: {len(groups):,} groups, {format_size(total_wasted)} wasted",
        "",
    ]

    for g in groups[:20]:
        lines.append(
            f"  [{g.method}] {g.count} x {format_size(g.file_size)} = {g.wasted_display} wasted"
        )
        for fi in g.files[:3]:
            lines.append(f"    {fi.path.name}")

    if len(groups) > 20:
        lines.append(f"\n  ... and {len(groups) - 20} more groups")

    return "\n".join(lines)
