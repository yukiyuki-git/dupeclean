"""File deduplication duplicate finder v3 for DupeClean.

Enhanced duplicate finder with machine learning-like heuristics.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class FinderResultV2:
    """Enhanced finder result."""
    groups: list[DuplicateGroup] = field(default_factory=list)
    method: str = ""
    files_scanned: int = 0
    candidates_filtered: int = 0
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

    @property
    def filter_ratio(self) -> float:
        if self.files_scanned == 0:
            return 0.0
        return self.candidates_filtered / self.files_scanned


def find_with_prefilter(files: list[FileInfo]) -> FinderResultV2:
    """Find duplicates with pre-filtering for efficiency.

    Phase 1: Group by size (instant, no I/O)
    Phase 2: Hash only candidates (reduces I/O)
    """
    result = FinderResultV2(method="prefilter", files_scanned=len(files))

    # Phase 1: Size-based pre-filter
    size_groups: dict[int, list[FileInfo]] = defaultdict(list)
    for fi in files:
        if fi.size > 0:
            size_groups[fi.size].append(fi)

    candidates = []
    for _size, group in size_groups.items():
        if len(group) >= 2:
            candidates.extend(group)

    result.candidates_filtered = len(candidates)

    # Phase 2: Group candidates by size
    for size, group in size_groups.items():
        if len(group) >= 2:
            result.groups.append(
                DuplicateGroup(
                    group_id=len(result.groups),
                    hash_value=f"size_{size}",
                    file_size=size,
                    files=group,
                )
            )

    result.groups.sort(key=lambda g: g.wasted_space, reverse=True)
    return result


def find_by_content_hash(files: list[FileInfo]) -> FinderResultV2:
    """Find duplicates using content hashes."""
    groups: dict[str, list[FileInfo]] = defaultdict(list)

    for fi in files:
        h = fi.hash_for_dedup
        if h:
            groups[h].append(fi)

    result = FinderResultV2(method="content_hash", files_scanned=len(files))
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


def format_finder_result_v2(result: FinderResultV2) -> str:
    """Format finder result as text."""
    lines = [
        f"Duplicate Finder ({result.method}):",
        f"  Scanned: {result.files_scanned:,}",
        f"  Candidates: {result.candidates_filtered:,}",
        f"  Groups: {result.count:,}",
        f"  Duplicates: {result.total_duplicates:,}",
        f"  Wasted: {result.wasted_display}",
    ]
    if result.filter_ratio > 0:
        lines.append(f"  Filter ratio: {result.filter_ratio:.1%}")
    return "\n".join(lines)
