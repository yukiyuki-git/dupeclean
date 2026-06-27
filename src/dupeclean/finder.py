"""File deduplication duplicate finder module for DupeClean.

Find duplicate files using various strategies.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class FindResult:
    """Result of duplicate finding."""

    groups: list[DuplicateGroup] = field(default_factory=list)
    method: str = ""
    duration: float = 0.0

    @property
    def count(self) -> int:
        return len(self.groups)

    @property
    def total_duplicates(self) -> int:
        return sum(g.count for g in self.groups)

    @property
    def total_wasted(self) -> int:
        return sum(g.wasted_space for g in self.groups)

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)


def find_by_size(files: list[FileInfo]) -> FindResult:
    """Find potential duplicates by file size."""
    groups: dict[int, list[FileInfo]] = defaultdict(list)
    for fi in files:
        if fi.size > 0:
            groups[fi.size].append(fi)

    result = FindResult(method="size")
    for size, group_files in groups.items():
        if len(group_files) >= 2:
            result.groups.append(
                DuplicateGroup(
                    group_id=len(result.groups),
                    hash_value=f"size_{size}",
                    file_size=size,
                    files=group_files,
                )
            )

    result.groups.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def find_by_hash(files: list[FileInfo]) -> FindResult:
    """Find confirmed duplicates by hash."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)
    for fi in files:
        h = fi.hash_for_dedup
        if h:
            groups[h].append(fi)

    result = FindResult(method="hash")
    for hash_val, group_files in groups.items():
        if len(group_files) >= 2:
            result.groups.append(
                DuplicateGroup(
                    group_id=len(result.groups),
                    hash_value=hash_val,
                    file_size=group_files[0].size,
                    files=group_files,
                )
            )

    result.groups.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def format_find_result(result: FindResult) -> str:
    """Format find result as text."""
    return (
        f"Duplicates ({result.method}): {result.count} groups, "
        f"{result.total_duplicates} files, "
        f"{result.wasted_display} wasted"
    )
