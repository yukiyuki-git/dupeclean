"""File deduplication duplicate finder v2 for DupeClean.

Enhanced duplicate finding with multiple strategies.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class FinderResult:
    """Result of duplicate finding."""

    groups: list[DuplicateGroup] = field(default_factory=list)
    method: str = ""
    files_scanned: int = 0
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


def find_by_size_and_name(files: list[FileInfo]) -> FinderResult:
    """Find potential duplicates by size and name similarity."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)

    for fi in files:
        if fi.size > 0:
            # Group by size + normalized name
            key = f"{fi.size}_{fi.path.stem.lower()}"
            groups[key].append(fi)

    result = FinderResult(method="size+name", files_scanned=len(files))
    for key, group_files in groups.items():
        if len(group_files) >= 2:
            result.groups.append(
                DuplicateGroup(
                    group_id=len(result.groups),
                    hash_value=key,
                    file_size=group_files[0].size,
                    files=group_files,
                )
            )

    result.groups.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def find_by_partial_hash(
    files: list[FileInfo],
) -> FinderResult:
    """Find duplicates using partial file hashes."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)

    for fi in files:
        h = fi.quick_hash or fi.hash_for_dedup
        if h:
            groups[h].append(fi)

    result = FinderResult(method="partial_hash", files_scanned=len(files))
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


def format_finder_result(result: FinderResult) -> str:
    """Format finder result as text."""
    return (
        f"Duplicates ({result.method}): "
        f"{result.count} groups, "
        f"{result.total_duplicates} files, "
        f"{result.wasted_display} wasted"
    )
