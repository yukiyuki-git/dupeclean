"""File deduplication group merger for DupeClean.

Merge duplicate groups that share common files.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DuplicateGroup, FileInfo


@dataclass
class MergeResult:
    """Result of merging groups."""

    original_count: int = 0
    merged_count: int = 0
    groups_merged: int = 0
    files_deduped: int = 0

    @property
    def reduction(self) -> int:
        return self.original_count - self.merged_count

    @property
    def reduction_pct(self) -> float:
        if self.original_count == 0:
            return 0.0
        return (self.reduction / self.original_count) * 100


def merge_overlapping_groups(
    groups: list[DuplicateGroup],
) -> tuple[list[DuplicateGroup], MergeResult]:
    """Merge groups that share common files.

    Groups with overlapping file sets are merged into
    single larger groups.
    """
    result = MergeResult(original_count=len(groups))

    # Build file -> group index
    file_to_group: dict[str, set[int]] = {}
    for i, group in enumerate(groups):
        for fi in group.files:
            key = str(fi.path)
            file_to_group.setdefault(key, set()).add(i)

    # Find connected components
    visited = set()
    merged_groups: list[set[int]] = []

    for i in range(len(groups)):
        if i in visited:
            continue
        component = set()
        stack = [i]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            for fi in groups[current].files:
                for neighbor in file_to_group.get(str(fi.path), set()):
                    if neighbor not in visited:
                        stack.append(neighbor)
        merged_groups.append(component)

    # Build merged groups
    new_groups: list[DuplicateGroup] = []
    for component in merged_groups:
        all_files: list[FileInfo] = []
        for idx in component:
            all_files.extend(groups[idx].files)

        # Deduplicate files by path
        seen_paths: dict[str, FileInfo] = {}
        for fi in all_files:
            key = str(fi.path)
            if key not in seen_paths:
                seen_paths[key] = fi

        unique_files = list(seen_paths.values())
        if len(unique_files) >= 2:
            file_size = unique_files[0].size
            new_groups.append(
                DuplicateGroup(
                    group_id=len(new_groups),
                    hash_value=groups[next(iter(component))].hash_value,
                    file_size=file_size,
                    files=unique_files,
                )
            )

    result.merged_count = len(new_groups)
    result.groups_merged = sum(1 for g in merged_groups if len(g) > 1)

    return new_groups, result


def format_merge_result(result: MergeResult) -> str:
    """Format merge result as text."""
    return (
        f"Merge: {result.original_count} -> {result.merged_count} groups "
        f"({result.groups_merged} merged, "
        f"{result.reduction_pct:.1f}% reduction)"
    )
